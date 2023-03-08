
# Aplicación web para mostrar datos actualizados de un E-Commerce de Shopify

Aplicación Django para sincronizar los datos de Artículos (Productos) y Compras (Órdenes pagadas) desde un E-Commerce en la plataforma Shopify hacia una Base de datos local.



## Features

- Sincronización de inventario
- Sincronización de ventas


## Tech Stack

- **Backend:** Django (Python 3.10.0)

- **Database:** MySQL

- **Frontend:** HTML, CSS, JavaScript

## Instalación

Crear un nuevo directorio.

```bash
  mkdir mi-proyecto
  cd mi-proyecto
```

Dentro del directorio, crea un Virtual Environment para manejar el desarrollo de la aplicación Django.

```bash
  python3 -m venv venv
```

Luego, activa el Virtual Environment. En Linux:

```bash
  source venv/bin/activate
```

En Windows:

```bash
  source venv/Scripts/activate
```

Una vez activado en Virtual Environment, crea un nuevo directorio que alojará la aplicación Django.

```bash
  mkdir arstore
  cd arstore
```

Clona o descarga el ZIP de la aplicación Django de este repositorio y guárdala dentro del directorio creado en el paso anterior (Ej: arstore).

El proyecto debería verse así:

```bash
  mi-proyecto
  -- arstore
  ---- arstore
  ---- catalogo
  ---- compras
  ---- static
  ---- templates
  ---- .env.example
  ---- .gitignore
  ---- manage.py
  ---- requirements.txt
  -- venv
```

Ahora, debemos instalar Django y el resto de packages utilizados en este proyecto.

```bash
  pip install Django==4.1.7
  pip install -r requirements.txt
```

Debemos crear un archivo .env (o reemplazar el archivo .env.example por el .env) y llenar los campos propuestos (sin comillas, aunque sean strings, y sin corchetes o llaves, aunque sean arrays u objetos):

```bash
  DEBUG=True
  SECRET_KEY=
  ALLOWED_HOSTS=localhost,127.0.0.1,.ngrok.io
  DB_ENGINE=django.db.backends.mysql
  DB_NAME=mydatabaseName
  DB_USER=mydatabaseUser
  DB_PASSWORD=mydatabasePassword
  DB_HOST=localhost
  DB_PORT=3306
```

Para obtener un nuevo ```SECRET_KEY```, accedemos al django-admin shell desde la línea de comandos:

```bash
  django-admin shell
  >> from django.core.management.utils import get_random_secret_key
  >> get_random_secret_key()
```

Copiamos el string (sin las comillas que lo envuelven) que nos devuelve la función get_random_secret_key() y lo añadimos en el archivo .env, en la variable ```SECRET_KEY``` (Para salir del shell, colocamos el comando exit()).

Recuerda reemplazar las variables de la base de datos con los datos de tu propia base de datos.

Une vez hecho esto, podemos conectar nuestra aplicación Django con la base de datos. Las tablas definidas en el proyecto se crearán automáticamente.

```bash
  python manage.py makemigrations
  python manage.py migrate
```

Por último, levantamos la aplicación en el servidor web de desarrollo provisto por Django, que por defecto corre en el puerto 8000 de la IP 127.0.0.1.

```bash
  python manage.py runserver
```

Listo, ahora deberías ver la aplicación, aunque todavía no tengas los datos sincronizados de tu E-commerce en Shopify. En el siguiente paso, lo resolveremos.
## Conexión con Shopify

En el archivo .env, debemos obtener los datos que nos faltan de nuestra E-Commerce en Shopify.

```bash
  SHOPIFY_SHOP_URL=mitiendaenlinea.myshopify.com
  SHOPIFY_API_VERSION=2023-01
  SHOPIFY_ADMIN_API_ACCESS_TOKEN=
  SHOPIFY_API_KEY=
  SHOPIFY_SECRET_KEY=
  CLIENT_SECRET=
```

Para realizar una primera carga de los datos almacenados en nuestro E-Commerce hacia nuestra base de datos local, nos conectaremos al E-Commerce usando el package ShopifyAPI, instalado en la aplicación Django. Para eso, debemos obtener los valores de las variables ```SHOPIFY_SHOP_URL```, ```SHOPIFY_API_VERSION``` y ```SHOPIFY_ADMIN_API_ACCESS_TOKEN``` (las variables ```SHOPIFY_API_KEY``` y ```SHOPIFY_SECRET_KEY``` no son indispensables para este proyecto, pero su uso va a depender del tipo de cuenta que tengas en Shopify).

Primero, creamos una app en Shopify. Vamos a:
- Settings -> Apps and sales channels -> Develop apps -> Create an app
- Colocas un nombre para la app, eliges los permisos necesarios (scopes o alcances) y la version que vas a usar (Ej: 2023-01)

Para este proyecto, los scopes necesarios son: 
- read_assigned_fulfillment_orders
- read_files
- read_inventory
- read_orders
- read_product_listings
- read_products

Una vez creada la app en Shopify, puedes obtener los valores de las variables ```SHOPIFY_ADMIN_API_ACCESS_TOKEN```, ```SHOPIFY_API_KEY``` y ```SHOPIFY_SECRET_KEY```.

El valor de la variable ```SHOPIFY_SHOP_URL``` es la URL de tu cuenta de Shopify.

Listo, con esas variables ya se puede realizar la primera carga de los datos (tanto de los Artículos/Productos como de las Órdenes pagadas) a tu base de datos local. Después de llenar los valores de esas variables tendrás que reiniciar el servidor web de desarrollo.

```bash
  CTRL-C
  python manage.py runserver
```

Ahora solo nos queda configurar los WebHooks de Shopify para sincronizar el inventario y las compras cuando:
- Se añada un nuevo producto.
- Se actualice un producto.
- Se elimine un producto.
- Se pague una orden de compra.

Para eso, primero debemos instalar e iniciar ngrok (en otra línea de comandos):

```bash
  ngrok http 8000
```

Al iniciar ngrok, nos va a proveer de una URL con certificado SSL (necesario para probar el webhook) que redirige a nuestra aplicación Django que está corriendo en el localhost, en el puerto 8000.

```bash
  Forwarding    https://numerorandom.ngrok.io -> http://localhost:8000
```

Una vez iniciado ngrok, debemos ir a Shopify -> Settings -> Notifications -> Webhooks -> Create webhook. Los Webhooks que debemos crear son:

- Product creation: https://numerorandom.ngrok.io/catalogo/webhook/new
- Product update: https://numerorandom.ngrok.io/catalogo/webhook/update
- Product deletion: https://numerorandom.ngrok.io/catalogo/webhook/delete
- Order payment: https://numerorandom.ngrok.io/compras/webhook/new

No olvides elegir el formato ```JSON``` y la versión del API ```2023-01```.

Por último, el valor de la variable ```CLIENT_SECRET``` aparece en la parte inferior de la lista de Webhooks creados: "*All your webhooks will be signed with ```CLIENT_SECRET``` so you can verify their integrity.*" Este valor es necesario para el paso de verificación de los WebHooks.

Finalmente, reinicia el servidor web de desarrollo.

```bash
  CTRL-C
  python manage.py runserver
```

Y, listo. La aplicación Django está lista para escuchar los eventos de tu E-Commerce en Shopify, al crear, actualizar y eliminar un producto, y al momento de que una orden sea pagada.
## Deployment

Para desplegar la aplicación Django en un servidor.

Esta sección está en construcción.


## Documentation

- [Django documentation](https://docs.djangoproject.com/)
- [Shopify WebHooks](https://shopify.dev/api/admin-rest/2022-04/resources/webhook)
- [ngrok documentation](https://ngrok.com/)
