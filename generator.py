def generate_pandas_code(parsed: dict) -> str:
    lines = ["import pandas as pd", ""]
    step = 1

    # 1. Subquery
    if parsed.get("subquery"):
        s = parsed["subquery"]
        lines.append(f"# PASO {step}: Procesar subconsulta '{s['alias']}'")
        f = f".query(\"{s['filters']}\")" if s['filters'] else ""
        lines.append(f"df_sub = {s['table']}{f}.groupby('{s['right_key']}')['{s['target_col']}'].{s['operation']}().reset_index()")
        lines.append(f"df_sub.columns = ['{s['right_key']}', '{s['alias']}']")
        step += 1

    # 2. Carga y Merges (Join de tablas principales o subqueries)
    lines.append(f"\n# PASO {step}: Cargar tabla principal")
    lines.append(f"df = {parsed['base_table']}.copy()")
    step += 1

    if parsed.get("joins"):
        for j_table in parsed["joins"]:
            lines.append(f"df = df.merge({j_table}, on='customer_id', how='inner') # Join detectado")
    
    if parsed.get("subquery"):
        s = parsed["subquery"]
        lines.append(f"df = df.merge(df_sub, left_on='{s['left_key']}', right_on='{s['right_key']}', how='left')")

    # 3. Filtros
    if parsed.get("where"):
        w = parsed["where"]
        lines.append(f"\n# PASO {step}: Filtrar registros")
        engine = ", engine='python'" if ".str." in w else ""
        lines.append(f"df = df.query(\"\"\"{w}\"\"\"{engine})")
        step += 1

    # 4. Agregación (GROUP BY) o Renombrado (Alias simples)
    if parsed.get("group_by"):
        lines.append(f"\n# PASO {step}: Agrupar y Agregar")
        agg_items = [f"{alias}=('{col}', '{op}')" for alias, (col, op) in parsed["aggregations"].items()]
        lines.append(f"df = df.groupby({parsed['group_by']}).agg({', '.join(agg_items)}).reset_index()")
        step += 1
    elif parsed.get("rename_map"):
        lines.append(f"\n# PASO {step}: Renombrar columnas")
        lines.append(f"df = df.rename(columns={parsed['rename_map']})")
        step += 1

    # 5. Orden y Limit
    if parsed.get("order_by"):
        o = parsed["order_by"]
        lines.append(f"\n# PASO {step}: Ordenar")
        lines.append(f"df = df.sort_values(by='{o['column']}', ascending={o['ascending']})")
        step += 1
    
    if parsed.get("limit"):
        lines.append(f"df = df.head({parsed['limit']})")
        step += 1

    # 6. Selección final
    cols = ", ".join([f"'{c}'" for c in parsed["select"]])
    lines.append(f"\n# PASO {step}: Selección final")
    lines.append(f"df = df[[{cols}]]")

    return "\n".join(lines)