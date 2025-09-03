from database.mongo import db

brews_db = db["brews"]


def get_all_brews ():
    all_brews_cursor = brews_db.find({})

    brews_list = []
    for brew in all_brews_cursor:
        brew["_id"] = str(brew["_id"])
        brews_list.append(brew)

    return{
        "brews": brews_list,
    }



def search_brews(search=None, style=None, min_abv=None, max_abv=None, min_price=None, max_price=None):
    """Busca y filtra cervezas según los parámetros dados"""
    try:
        print(f"=== DEBUG SEARCH BREWS ===")
        print(
            f"Parámetros: search={search}, style={style}, min_abv={min_abv}, max_abv={max_abv}, min_price={min_price}, max_price={max_price}")

        # Construir query dinámicamente
        query = {}

        # Filtro de búsqueda por texto (nombre o descripción)
        if search:
            query["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}}
            ]

        # Filtro por estilo
        if style:
            query["style"] = {"$regex": style, "$options": "i"}

        # Filtros por ABV
        if min_abv is not None or max_abv is not None:
            query["abv"] = {}
            if min_abv is not None:
                query["abv"]["$gte"] = min_abv
            if max_abv is not None:
                query["abv"]["$lte"] = max_abv

        # Filtros por precio
        if min_price is not None or max_price is not None:
            query["price"] = {}
            if min_price is not None:
                query["price"]["$gte"] = min_price
            if max_price is not None:
                query["price"]["$lte"] = max_price

        print(f"Query construida: {query}")

        # Ejecutar búsqueda
        brews_cursor = brews_db.find(query).sort("name", 1)  # Ordenar por nombre
        brews_list = []

        for brew in brews_cursor:
            brew["_id"] = str(brew["_id"])
            if "id_user" in brew:
                brew["id_user"] = str(brew["id_user"]) if brew["id_user"] else None
            brews_list.append(brew)

        print(f"Cervezas encontradas: {len(brews_list)}")

        return {
            "message": "Brews retrieved successfully",
            "brews": brews_list,
            "total_results": len(brews_list),
            "filters_applied": {
                "search": search,
                "style": style,
                "abv_range": f"{min_abv}-{max_abv}" if min_abv or max_abv else None,
                "price_range": f"{min_price}-{max_price}" if min_price or max_price else None
            }
        }

    except Exception as e:
        print(f"Error en search_brews: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


def get_unique_brew_styles():
    """Obtiene todos los estilos únicos de cerveza para usar en filtros"""
    try:
        # Obtener estilos únicos
        unique_styles = brews_db.distinct("style")
        # Filtrar valores vacíos o None
        unique_styles = [style for style in unique_styles if style and style.strip()]
        # Ordenar alfabéticamente
        unique_styles.sort()

        print(f"Estilos únicos encontrados: {len(unique_styles)}")

        return {
            "message": "Unique styles retrieved successfully",
            "styles": unique_styles,
            "total_styles": len(unique_styles)
        }

    except Exception as e:
        print(f"Error en get_unique_brew_styles: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")