import os, environ, base64, hashlib, hmac, json
from pathlib import Path
from django.shortcuts import render
import shopify
from catalogo.models import Articulo
from .models import Encabezado, Detalle, Cliente
from datetime import datetime
from currency_symbols import CurrencySymbols
from django.http import HttpResponse, HttpResponseBadRequest 
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

#environ init
BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

def compras(request):
    template = 'compras/compras.html'

    default_page = 1
    page = request.GET.get('page', default_page)

    numOrdenesDB = Encabezado.objects.count()
    numOrdenesShopify = countOrdersFromShopify()
    if numOrdenesDB < numOrdenesShopify:
        loaded = loadAllOrdenesFromShopifyToDB()
    
    ordenes = Encabezado.objects.all().order_by('-numeroOrden')
    ordenes_per_page = 10
    paginator = Paginator(ordenes, ordenes_per_page)
    
    try:
        ordenes_page = paginator.page(page)
    except PageNotAnInteger:
        ordenes_page = paginator.page(default_page)
    except EmptyPage:
        ordenes_page = paginator.page(paginator.num_pages)

    currencySymbol = CurrencySymbols.get_symbol(str(ordenes[0].moneda))

    context = {
        'ordenes_page': ordenes_page,
        'currencySymbol': currencySymbol,
        'totalOrdenes': len(ordenes)
    }

    return render(request, template, context)

def orden(request, idOrden):
    template = 'compras/orden.html'

    orden = None
    detalles = []
    currencySymbol = ''
    try:
        orden = Encabezado.objects.get(id=idOrden)
        detalles = Detalle.objects.filter(encabezado=orden)
        currencySymbol = CurrencySymbols.get_symbol(str(orden.moneda))
    except Exception as e:
        print(f'Exception in orden: {e}')

    context = {
        'orden': orden,
        'detalles': detalles,
        'currencySymbol': currencySymbol
    }
    return render(request, template, context)

@csrf_exempt
def webhookOrderPaid(request):
    data = request.body
    verified = verifyWebhook(data, request.headers['X-Shopify-Hmac-SHA256'])
    if not verified:
        return HttpResponseBadRequest()

    saveOrderToDB(json.loads(data))

    return HttpResponse()

def verifyWebhook(data, hmac_header):
    digest = hmac.new(env.str('CLIENT_SECRET').encode('utf-8'), data, digestmod=hashlib.sha256).digest()
    computed_hmac = base64.b64encode(digest)

    return hmac.compare_digest(computed_hmac, hmac_header.encode('utf-8'))

def loadAllOrdenesFromShopifyToDB():
    try:
        openConnectionToShopify()
        
        orders = shopify.Order.find(financial_status='paid')
        ordersDict = [o.to_dict() for o in orders]
        for o in ordersDict:
            saveOrderToDB(o)
            
    except Exception as e:
        print(f'Exception in loadAllOrdenesFromShopifyToDB: {e}')
        return False
    finally:
        closeConnectionToShopify()

    return True

def saveOrderToDB(orden):
    try:
        ordenesDB = Encabezado.objects.filter(orden_id=orden['id'])
        
        if len(ordenesDB) == 0:
            nuevaOrden, created = Encabezado.objects.get_or_create(
                numeroOrden = orden['name'],
                total = orden['total_price'],
                fechaRegistro = datetime.fromisoformat(orden['created_at']),
                moneda = orden['currency'],
                fechaActualizacion = datetime.fromisoformat(orden['updated_at']),
                orden_id = orden['id']
            )
            if created:
                nuevaOrden.save()
                # Save cliente
                nombre, telefono, correo, direccion = '', '', '', ''
                if 'customer' in orden and orden['customer'] is not None:
                    nombre = (orden['customer']['first_name'] if orden['customer']['first_name'] is not None else '') + ' ' +  (orden['customer']['last_name'] if orden['customer']['last_name'] is not None else '')
                    telefono = orden['billing_address']['phone'] if orden['billing_address']['phone'] is not None  else ''
                    correo = orden['customer']['email'] if orden['customer']['email'] is not None else ''
                    direccion = orden['customer']['default_address']['address1'] if orden['customer']['default_address'] is not None else ''
                if 'billing_address' in orden and orden['billing_address'] is not None:
                    nombre = orden['billing_address']['name'] if nombre == '' and orden['billing_address']['name'] is not None else nombre
                    telefono = orden['billing_address']['phone'] if telefono == '' and orden['billing_address']['phone'] is not None else telefono
                    if direccion == '' or direccion is None:
                        direccion = str(orden['billing_address']['address1'] or '') + str(orden['billing_address']['address2'] or '')
                
                cliente = Cliente.objects.create(
                    encabezado = nuevaOrden,
                    nombre = nombre,
                    telefono = telefono,
                    correo = correo,
                    direccion = direccion
                )
                cliente.save()

                # Save items in detalle
                for item in orden['line_items']:
                    imagenURI = None
                    if item['product_id'] is not None:
                        articulo = Articulo.objects.filter(product_id=item['product_id'])
                        imagenURI = articulo[0].imagenURI if len(articulo) > 0 else None
                    elif item['sku'] is not None:
                        articulo = Articulo.objects.filter(sku=item['product_id'])
                        imagenURI = articulo[0].imagenURI if len(articulo) > 0 else None

                    detalle = Detalle.objects.create(
                        encabezado = nuevaOrden,
                        sku = item['sku'],
                        nombre = item['name'],
                        cantidad = item['quantity'],
                        precio = item['price'],
                        total = float(item['price']) * float(item['quantity']),
                        product_id = item['product_id'],
                        imagenURI = imagenURI
                    )
                    detalle.save()

    except Exception as e:
        print(f'Exception in saveOrderToDB: {e}')
        return False
    return True

def countOrdersFromShopify():
    count = 0
    try:
        openConnectionToShopify()
        count = shopify.Order.count(financial_status='paid')
    except Exception as e:
        print(f'Exception in countOrdersFromShopify: {e}')
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
