import os, environ, base64, hashlib, hmac, json
from pathlib import Path
from django.shortcuts import render
import shopify
from .models import Articulo, LogArticulo
from datetime import datetime
from django.http import HttpResponse, HttpResponseBadRequest 
from django.views.decorators.csrf import csrf_exempt

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

@csrf_exempt
def webhookProduct(request):
    data = request.body
    verified = verifyWebhook(data, request.headers['X-Shopify-Hmac-SHA256'])
    if not verified:
        return HttpResponseBadRequest()

    #Handle webhook json response
    #print(json.loads(data))
    saveProductToDB(json.loads(data))

    return HttpResponse()

def verifyWebhook(data, hmac_header):
    digest = hmac.new(env.str('CLIENT_SECRET').encode('utf-8'), data, digestmod=hashlib.sha256).digest()
    computed_hmac = base64.b64encode(digest)

    return hmac.compare_digest(computed_hmac, hmac_header.encode('utf-8'))


def loadAllArticulosFromDB():
    articulos = Articulo.objects.all()
    return articulos

def loadAllArticulosFromShopifyToDB():
    try:
        openConnectionToShopify()
        
        products = shopify.Product.find()
        productsDict = [p.to_dict() for p in products]
        for p in productsDict:
            saveProductToDB(p)
    except Exception as e:
        print(e)
        return False
    finally:
        closeConnectionToShopify()

    return True

def saveProductToDB(product):
    try:
        imageurl = None if product['image'] is None else product['image']['src']
        if 'variants' in product:
            for variant in product['variants']:
                articulos = Articulo.objects.filter(product_id=variant['id'])
                print(articulos)
                if len(articulos) == 0:
                    articulo, created = Articulo.objects.create(
                        sku = variant['sku'], 
                        imagenURI = imageurl,
                        nombre = product['title'] + ' ' + variant['title'],
                        cantidad = variant['inventory_quantity'],
                        fechaRegistro = datetime.fromisoformat(variant['created_at']),
                        ultimaFechaActualizacion = datetime.fromisoformat(variant['updated_at']),
                        product_id = variant['id']
                    )
                    if created:
                        articulo.save()
                        log = LogArticulo.objects.create(
                            articulo = articulo,
                            json = json.dumps({'articulo': variant})
                        )
                        log.save()
                else:
                    articulos[0].sku = variant['sku']
                    articulos[0].imagenURI = imageurl
                    articulos[0].nombre = product['title'] + ' ' + variant['title']
                    articulos[0].cantidad = variant['inventory_quantity']
                    articulos[0].fechaRegistro = datetime.fromisoformat(variant['created_at'])
                    articulos[0].ultimaFechaActualizacion = datetime.fromisoformat(variant['updated_at'])
                    articulos[0].save()
                    
                    log = LogArticulo.objects.create(
                        articulo = articulos[0],
                        json = json.dumps({'articulo': variant})
                    )
                    log.save()

    except Exception as e:
        print(e)
        return False
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
