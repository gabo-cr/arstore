import os, environ, base64, hashlib, hmac, json
from pathlib import Path
from django.shortcuts import render
import shopify
from .models import Articulo, LogArticulo
from datetime import datetime
from django.http import HttpResponse, HttpResponseBadRequest 
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

#environ init
BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

def catalogo(request):
    template = 'catalogo/catalogo.html'
    
    default_page = 1
    page = request.GET.get('page', default_page)

    numArticulosDB = Articulo.objects.count()
    numArticulosShopify = countProductsFromShopify()
    if numArticulosDB < numArticulosShopify:
        loaded = loadAllArticulosFromShopifyToDB()
    
    articulos = Articulo.objects.all().order_by('-ultimaFechaActualizacion')
    articulos_per_page = 5
    paginator = Paginator(articulos, articulos_per_page)

    try:
        articulos_page = paginator.page(page)
    except PageNotAnInteger:
        articulos_page = paginator.page(default_page)
    except EmptyPage:
        articulos_page = paginator.page(paginator.num_pages)
    
    context = {
        'articulos_page': articulos_page,
        'totalArticulos': len(articulos)
    }
    return render(request, template, context)

@csrf_exempt
def webhookProduct(request):
    data = request.body
    verified = verifyWebhook(data, request.headers['X-Shopify-Hmac-SHA256'])
    if not verified:
        return HttpResponseBadRequest()

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
        articulosDB = Articulo.objects.filter(product_id=product['id'])
        imageurl = None if product['image'] is None else product['image']['src']
        
        cantidad = 0
        for variant in product['variants']:
            cantidad += int(variant['inventory_quantity'])
            sku = str(variant['sku'])

        if len(articulosDB) == 0:
            articulo, created = Articulo.objects.get_or_create(
                sku = sku, 
                imagenURI = imageurl,
                nombre = product['title'],
                cantidad = cantidad,
                fechaRegistro = datetime.fromisoformat(product['created_at']),
                ultimaFechaActualizacion = datetime.fromisoformat(product['updated_at']),
                product_id = product['id']
            )
            if created:
                articulo.save()
                log = LogArticulo.objects.create(
                    articulo = articulo,
                    json = json.dumps({'product': json.dumps(product)})
                )
                log.save()
        else:
            articulosDB[0].sku = sku
            articulosDB[0].imagenURI = imageurl
            articulosDB[0].nombre = product['title']
            articulosDB[0].cantidad = cantidad
            articulosDB[0].fechaRegistro = datetime.fromisoformat(product['created_at'])
            articulosDB[0].ultimaFechaActualizacion = datetime.fromisoformat(product['updated_at'])
            articulosDB[0].save()
            
            log = LogArticulo.objects.create(
                articulo = articulosDB[0],
                json = json.dumps({'articulo': json.dumps(product)})
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
        count = shopify.Product.count()
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
