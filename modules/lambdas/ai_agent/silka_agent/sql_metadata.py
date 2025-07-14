import re


def extract_sql_metadata_regex(sql_query: str) -> dict:
    """Extract tables and columns using regex patterns, excluding aliases."""
    tables = set()
    columns = set()

    # Extract table names from FROM and JOIN clauses (excluding aliases)
    from_pattern = r"FROM\s+([a-zA-Z_][a-zA-Z0-9_]*)"
    join_pattern = r"JOIN\s+([a-zA-Z_][a-zA-Z0-9_]*)"

    from_matches = re.findall(from_pattern, sql_query, re.IGNORECASE)
    join_matches = re.findall(join_pattern, sql_query, re.IGNORECASE)

    tables.update(from_matches)
    tables.update(join_matches)

    # Build alias mapping to exclude them
    alias_pattern = r"FROM\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+([a-zA-Z_][a-zA-Z0-9_]*)|JOIN\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+([a-zA-Z_][a-zA-Z0-9_]*)"
    alias_matches = re.findall(alias_pattern, sql_query, re.IGNORECASE)

    # Create set of known aliases
    aliases = set()
    for match in alias_matches:
        if match[1]:  # FROM table alias
            aliases.add(match[1])
        if match[3]:  # JOIN table alias
            aliases.add(match[3])

    # Extract column names from table.column patterns (excluding aliases)
    column_pattern = r"\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\.\s*([a-zA-Z_][a-zA-Z0-9_]*)"
    table_column_matches = re.findall(column_pattern, sql_query)

    for table_alias, column in table_column_matches:
        if table_alias not in ("DATE", "FROM_UNIXTIME", "CAST", "LOWER", "SUM"):
            # Only add the column, never add aliases to columns
            columns.add(column)
            # Only add table name if it's not an alias
            if table_alias not in aliases:
                tables.add(table_alias)

    # Extract standalone column names from SELECT (excluding AS aliases and table.column patterns)
    select_pattern = r"SELECT\s+(.*?)\s+FROM"
    select_match = re.search(select_pattern, sql_query, re.IGNORECASE | re.DOTALL)
    if select_match:
        select_clause = select_match.group(1)

        # Remove AS aliases from select clause
        select_clause = re.sub(
            r"\s+AS\s+[a-zA-Z_][a-zA-Z0-9_]*", "", select_clause, flags=re.IGNORECASE
        )

        # Remove table.column patterns to avoid picking up table aliases
        select_clause = re.sub(
            r"\b[a-zA-Z_][a-zA-Z0-9_]*\s*\.\s*[a-zA-Z_][a-zA-Z0-9_]*", "", select_clause
        )

        # Extract simple column names (standalone, not prefixed)
        simple_columns = re.findall(r"\b([a-zA-Z_][a-zA-Z0-9_]*)\b", select_clause)
        for col in simple_columns:
            if (
                col.upper()
                not in (
                    "DATE",
                    "FROM_UNIXTIME",
                    "CAST",
                    "AS",
                    "DOUBLE",
                    "SUM",
                    "LOWER",
                    "TOTAL_VOLUME",
                )
                and col not in aliases  # Exclude known aliases
            ):
                columns.add(col)

    return {
        "tables_used": list(tables),
        "columns_used": list(columns),
        "query_type": ["SELECT"],
    }
