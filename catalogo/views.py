import os, environ
from pathlib import Path
from django.shortcuts import render
import shopify
from .models import Articulo, LogArticulo
from datetime import datetime
import json

#environ init
BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

def catalogo(request):
    template = 'catalogo/catalogo.html'
    
    numArticulosDB = Articulo.objects.count()
    numArticulosShopify = countProductsFromShopify()
    if numArticulosDB < numArticulosShopify:
        loaded = loadAllArticulosFromShopifyToDB()
    
    articulos = Articulo.objects.all()
    
    context = {
        'articulos': articulos
    }
    return render(request, template, context)

def loadAllArticulosFromDB():
    articulos = Articulo.objects.all()
    return articulos

def loadAllArticulosFromShopifyToDB():
    try:
        openConnectionToShopify()
        
        products = shopify.Product.find()
        productsDict = [p.to_dict() for p in products]
        for p in productsDict:
            imageurl = None if p['image'] is None else p['image']['src']
            if 'variants' in p:
                for variant in p['variants']:
                    articulo, created = Articulo.objects.update_or_create(
                        sku=variant['sku'], 
                        imagenURI=imageurl,
                        nombre=p['title'] + ' ' + variant['title'],
                        cantidad=variant['inventory_quantity'],
                        fechaRegistro=datetime.fromisoformat(variant['created_at']),
                        ultimaFechaActualizacion=datetime.fromisoformat(variant['updated_at']),
                        product_id=variant['id']
                    )
                    if created:
                        articulo.save()
                        log = LogArticulo.objects.create(
                            articulo=articulo,
                            json=json.dumps({'articulo': variant})
                        )
                        log.save()
    except Exception as e:
        print(e)
        return False
    finally:
        closeConnectionToShopify()

    return True

def countProductsFromShopify():
    count = 0
    try:
        openConnectionToShopify()
        #count = shopify.Product.count()
        count = shopify.Variant.count()
    except Exception as e:
        print(e)
    finally:
        closeConnectionToShopify()
    return count

def openConnectionToShopify():
    shop_url = env.str('SHOPIFY_SHOP_URL')
    api_version = env.str('SHOPIFY_API_VERSION')
    token = env.str('SHOPIFY_ADMIN_API_ACCESS_TOKEN')
    
    api_session = shopify.Session(shop_url, api_version, token)
    shopify.ShopifyResource.activate_session(api_session)

def closeConnectionToShopify():
    shopify.ShopifyResource.clear_session()
