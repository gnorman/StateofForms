from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
import json
import os


# Backend API base URL
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8000')

def get_backend_url(request):
    """Get the correct backend URL based on how the frontend is accessed"""
    host = request.get_host()
    
    # If accessed via localhost, use container name for internal communication
    if 'localhost' in host or '127.0.0.1' in host:
        return BACKEND_URL  # Uses container name
    else:
        # If accessed via external IP, use the same IP for backend
        if ':' in host:
            server_ip = host.split(':')[0]
        else:
            server_ip = host
        return f'http://{server_ip}:8000'


def index(request):
    """Homepage view"""
    return render(request, 'core/index.html')


def dashboard(request):
    """Dashboard view with data overview"""
    try:
        # Fetch all queries from backend
        backend_url = get_backend_url(request)
        response = requests.get(f'{backend_url}/api/queries/')
        data = response.json() if response.status_code == 200 else {}
        
        return render(request, 'core/dashboard.html', {
            'data': data,
            'crypto_count': data.get('crypto_count', 0),
            'stock_count': data.get('stock_count', 0),
            'total_queries': data.get('total_queries', 0)
        })
    except requests.exceptions.RequestException as e:
        return render(request, 'core/dashboard.html', {
            'error': str(e),
            'crypto_count': 0,
            'stock_count': 0,
            'total_queries': 0
        })


def crypto_view(request):
    """Crypto data view"""
    return render(request, 'core/crypto.html')


def stocks_view(request):
    """Stocks data view"""
    return render(request, 'core/stocks.html')


@csrf_exempt
def api_proxy_crypto(request, path=''):
    """Proxy API calls to crypto backend"""
    try:
        backend_url = get_backend_url(request)
        url = f'{backend_url}/api/crypto/{path}'
        
        if request.method == 'GET':
            params = dict(request.GET.items())
            response = requests.get(url, params=params)
        elif request.method == 'POST':
            data = json.loads(request.body.decode('utf-8')) if request.body else {}
            response = requests.post(url, json=data)
        else:
            return JsonResponse({'error': 'Method not allowed'}, status=405)
            
        return JsonResponse(response.json(), status=response.status_code)
    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': str(e)}, status=500)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)


@csrf_exempt
def api_proxy_stock(request, path=''):
    """Proxy API calls to stock backend"""
    try:
        backend_url = get_backend_url(request)
        url = f'{backend_url}/api/stock/{path}'
        
        if request.method == 'GET':
            params = dict(request.GET.items())
            response = requests.get(url, params=params)
        elif request.method == 'POST':
            data = json.loads(request.body.decode('utf-8')) if request.body else {}
            response = requests.post(url, json=data)
        else:
            return JsonResponse({'error': 'Method not allowed'}, status=405)
            
        return JsonResponse(response.json(), status=response.status_code)
    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': str(e)}, status=500)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)


@csrf_exempt
def api_proxy_queries(request):
    """Proxy API calls to queries backend"""
    try:
        backend_url = get_backend_url(request)
        url = f'{backend_url}/api/queries/'
        
        if request.method == 'GET':
            params = dict(request.GET.items())
            response = requests.get(url, params=params)
        else:
            return JsonResponse({'error': 'Method not allowed'}, status=405)
            
        return JsonResponse(response.json(), status=response.status_code)
    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': str(e)}, status=500)


def health_check(request):
    """Health check endpoint"""
    try:
        backend_url = get_backend_url(request)
        response = requests.get(f'{backend_url}/ping-db', timeout=5)
        backend_status = response.status_code == 200
        backend_data = response.json() if backend_status else {}
        
        return JsonResponse({
            'status': 'healthy' if backend_status else 'unhealthy',
            'backend_connected': backend_status,
            'backend_response': backend_data,
            'backend_url': backend_url,  # Debug info
            'request_host': request.get_host()  # Debug info
        })
    except requests.exceptions.RequestException:
        return JsonResponse({
            'status': 'unhealthy',
            'backend_connected': False,
            'error': 'Backend not reachable',
            'backend_url': get_backend_url(request),  # Debug info
            'request_host': request.get_host()  # Debug info
        })