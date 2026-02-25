import sqlglot
from sqlglot import exp

def clean_name(name):
    """Limpia alias de tabla, esquemas y paréntesis residuales."""
    if not name: return name
    return name.split('.')[-1].replace(')', '').replace('(', '').strip()

def parse_sql(sql_query: str):
    tree = sqlglot.parse_one(sql_query, read="tsql")
    result = {
        "base_table": None, "select": [], "where": None, 
        "subquery": None, "order_by": None, "limit": None,
        "aliases": set(), "group_by": [], "aggregations": {}, 
        "rename_map": {}, "joins": []
    }

    # 1. Tabla Base y Alias
    from_exp = tree.find(exp.From)
    if from_exp:
        result["base_table"] = clean_name(from_exp.this.name)
        if from_exp.this.alias: result["aliases"].add(from_exp.this.alias)

    # 2. Joins (Detección básica para el Test 1)
    for join in tree.find_all(exp.Join):
        result["joins"].append(clean_name(join.this.name))
        if join.this.alias: result["aliases"].add(join.this.alias)

    # 3. SELECT: Agregaciones, Alias y Subqueries
    for projection in tree.expressions:
        alias = clean_name(projection.alias_or_name)
        
        # Caso A: Es una función agregada (COUNT, SUM...)
        agg_func = projection.find(exp.AggFunc)
        if agg_func:
            # Extraer la columna de adentro: SUM(o.amount) -> amount
            col_inside = clean_name(agg_func.this.sql())
            operation = agg_func.key.lower()
            result["aggregations"][alias] = (col_inside, operation)
        
        # Caso B: Es una Subquery
        elif projection.find(exp.Subquery):
            sub = projection.find(exp.Subquery).this
            from_sub = sub.find(exp.From)
            where_sub = sub.find(exp.Where)
            sub_alias = from_sub.this.alias_or_name
            
            sub_agg = sub.find(exp.AggFunc)
            t_col = clean_name(sub_agg.this.sql()) if sub_agg else clean_name(sub.find(exp.Column).sql())
            op = sub_agg.key.lower() if sub_agg else "first"

            left_k, right_k, sub_f = None, None, []
            if where_sub:
                for part in where_sub.this.flatten():
                    if isinstance(part, exp.EQ):
                        l_s, r_s = part.left.sql(), part.right.sql()
                        if "." in l_s and "." in r_s:
                            if l_s.startswith(f"{sub_alias}."):
                                left_k, right_k = clean_name(r_s), clean_name(l_s)
                            else:
                                left_k, right_k = clean_name(l_s), clean_name(r_s)
                        else:
                            sub_f.append(part.sql().replace("=", "==").replace(f"{sub_alias}.", ""))

            result["subquery"] = {
                "table": clean_name(from_sub.this.name),
                "left_key": left_k, "right_key": right_k,
                "target_col": t_col, "operation": op,
                "alias": alias, "filters": " & ".join(sub_f) if sub_f else None
            }
        
        # Caso C: Columna normal con posible Alias
        else:
            original_name = clean_name(projection.this.sql())
            if alias != original_name:
                result["rename_map"][original_name] = alias
        
        result["select"].append(alias)

    # 4. WHERE con soporte LIKE y limpieza de 'o.', 'c.', etc.
    where_main = tree.find(exp.Where)
    if where_main:
        for like_node in where_main.find_all(exp.Like):
            col = clean_name(like_node.left.sql())
            pattern = like_node.right.sql().replace("'", "")
            if pattern.endswith("%") and not pattern.startswith("%"):
                rep = f"{col}.str.startswith('{pattern[:-1]}')"
            elif pattern.startswith("%") and not pattern.endswith("%"):
                rep = f"{col}.str.endswith('{pattern[1:]}')"
            else:
                rep = f"{col}.str.contains('{pattern.replace('%', '')}')"
            like_node.replace(sqlglot.parse_one(rep))

        w_sql = where_main.this.sql()
        w_sql = w_sql.replace(">=", "T_GE").replace("<=", "T_LE").replace("=", "==").replace("T_GE", ">=").replace("T_LE", "<=")
        w_sql = w_sql.replace("AND", "&").replace("OR", "|")
        for a in result["aliases"]: w_sql = w_sql.replace(f"{a}.", "")
        result["where"] = w_sql

    # 5. GROUP BY, ORDER BY, LIMIT
    group_node = tree.find(exp.Group)
    if group_node:
        result["group_by"] = [clean_name(e.sql()) for e in group_node.expressions]

    order_node = tree.find(exp.Order)
    if order_node:
        o = order_node.expressions[0]
        col = clean_name(o.this.sql())
        for a in result["aliases"]: col = col.replace(f"{a}.", "")
        result["order_by"] = {"column": col, "ascending": "desc" not in o.sql().lower()}

    limit_node = tree.find(exp.Limit) or tree.args.get("limit")
    if limit_node: result["limit"] = limit_node.expression.sql()

    return result