import os, environ
from pathlib import Path
from django.shortcuts import render
import shopify
from .models import Encabezado, Detalle, Cliente
from datetime import datetime
from currency_symbols import CurrencySymbols

#environ init
BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

def compras(request):
    template = 'compras/compras.html'

    numOrdenesDB = Encabezado.objects.count()
    numOrdenesShopify = countOrdersFromShopify()
    if numOrdenesDB < numOrdenesShopify:
        loaded = loadAllOrdenesFromShopifyToDB()

    ordenes = Encabezado.objects.all()
    currencySymbol = CurrencySymbols.get_symbol(str(ordenes[0].moneda))
    context = {
        'ordenes': ordenes,
        'currencySymbol': currencySymbol
    }
    return render(request, template, context)

def orden(request, orden):
    template = 'compras/orden.html'
    context = {
        'orden': orden
    }
    return render(request, template, context)


def loadAllOrdenesFromDB():
    ordenes = Encabezado.objects.all()
    return ordenes

def loadAllOrdenesFromShopifyToDB():
    try:
        openConnectionToShopify()
        
        orders = shopify.Order.find()
        ordersDict = [o.to_dict() for o in orders]
        for o in ordersDict:
            if o['payment_terms'] is not None:
                fechaAct = next((i for i in o['payment_terms']['payment_schedules'] if i['completed_at'] is not None), None)
                if fechaAct is not None:
                    order, created = Encabezado.objects.update_or_create(
                        numeroOrden = o['name'],
                        total = o['total_price'],
                        fechaRegistro = datetime.fromisoformat(o['payment_terms']['created_at']),
                        moneda = o['currency'],
                        fechaActualizacion = datetime.fromisoformat(fechaAct['completed_at'])
                    )
                    if created:
                        order.save()
                        # Save cliente
                        direccion = o['billing_address']['address1'] if o['billing_address']['address2'] is None else o['billing_address']['address1'] + o['billing_address']['address2']
                        cliente, createdCliente = Cliente.objects.update_or_create(
                            encabezado = order,
                            nombre = o['billing_address']['name'],
                            telefono = o['billing_address']['phone'],
                            correo = o['customer']['email'],
                            direccion = direccion
                        )
                        if createdCliente:
                            cliente.save()

                        # Save items in detalle
                        for item in o['line_items']:
                            detalle, createdDetalle = Detalle.objects.update_or_create(
                                encabezado = order,
                                sku = item['sku'],
                                nombre = item['name'],
                                cantidad = item['quantity'],
                                precio = item['price'],
                                total = float(item['price']) * float(item['quantity']),
                                product_id = item['product_id']
                            )
                            if createdDetalle:
                                detalle.save()
                    
            
    except Exception as e:
        print(e)
        return False
    finally:
        closeConnectionToShopify()

    return True

def countOrdersFromShopify():
    count = 0
    try:
        openConnectionToShopify()
        #count = shopify.Order.count()
        count = 0
        orders = shopify.Order.find()
        ordersDict = [o.to_dict() for o in orders]
        for o in ordersDict:
            if o['payment_terms'] is not None:
                fechaAct = next((i for i in o['payment_terms']['payment_schedules'] if i['completed_at'] is not None), None)
                if fechaAct is not None:
                    count+=1
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
