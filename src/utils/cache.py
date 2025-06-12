from functools import wraps
from typing import Any, Callable, Dict, Optional, Tuple
import time
import hashlib
import json

# Cache en mémoire simple
cache_store: Dict[str, Tuple[float, Any]] = {}
DEFAULT_EXPIRY = 300  # 5 minutes


def cache_key(*args, **kwargs) -> str:
    """
    Génère une clé de cache à partir des arguments.
    """
    key_dict = {"args": args, "kwargs": kwargs}
    key_str = json.dumps(key_dict, sort_keys=True)
    return hashlib.md5(key_str.encode()).hexdigest()


def cache(expiry: int = DEFAULT_EXPIRY):
    """
    Décorateur pour mettre en cache le résultat d'une fonction.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Générer la clé de cache
            key = f"{func.__module__}.{func.__name__}:{cache_key(*args, **kwargs)}"
            
            # Vérifier si la valeur est dans le cache et n'a pas expiré
            now = time.time()
            if key in cache_store:
                expiry_time, value = cache_store[key]
                if expiry_time > now:
                    return value
            
            # Exécuter la fonction et mettre en cache le résultat
            result = func(*args, **kwargs)
            cache_store[key] = (now + expiry, result)
            
            return result
        return wrapper
    return decorator


def invalidate_cache(prefix: str = None) -> None:
    """
    Invalide le cache.
    """
    global cache_store
    if prefix:
        # Invalider uniquement les clés qui commencent par le préfixe
        cache_store = {k: v for k, v in cache_store.items() if not k.startswith(prefix)}
    else:
        # Invalider tout le cache
        cache_store = {}