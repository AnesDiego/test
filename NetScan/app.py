# Load environment variables FIRST
import os
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
import socket
import json
import requests
from ipwhois import IPWhois
from pytz import country_timezones, timezone
from datetime import datetime as dt, timedelta
import ipaddress
import re
import time
import threading
from functools import lru_cache
import csv
import io

# Production imports
from config import config
from firebase_service import init_firebase, get_firebase_service
from security import SecurityMiddleware, validate_ip_input, sanitize_output
from logging_config import setup_logging, log_user_activity, log_security_event, monitor_performance

app = Flask(__name__)

# Configuration based on environment
env = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[env])

# Initialize logging
loggers = setup_logging(app)

# Initialize security middleware
security = SecurityMiddleware(app)

# Initialize Firebase service
firebase_service = init_firebase(app.config)

app.secret_key = 'netscan_pro_2025_ultimate_secret_key'

# Configuration
OPENWEATHER_API_KEY = "your_openweather_api_key_here"  # Get from openweathermap.org

# Enhanced mappings
continent_map = {
    "US": "North America", "CA": "North America", "MX": "North America",
    "BR": "South America", "AR": "South America", "CL": "South America", 
    "CO": "South America", "PE": "South America", "VE": "South America",
    "UY": "South America", "PY": "South America", "EC": "South America",
    "GB": "Europe", "DE": "Europe", "FR": "Europe", "IT": "Europe", 
    "ES": "Europe", "NL": "Europe", "PL": "Europe", "RU": "Europe",
    "NO": "Europe", "SE": "Europe", "DK": "Europe", "FI": "Europe",
    "CN": "Asia", "IN": "Asia", "JP": "Asia", "KR": "Asia", "TH": "Asia",
    "ID": "Asia", "MY": "Asia", "SG": "Asia", "PH": "Asia", "VN": "Asia",
    "ZA": "Africa", "EG": "Africa", "NG": "Africa", "KE": "Africa", "MA": "Africa",
    "AU": "Oceania", "NZ": "Oceania", "FJ": "Oceania"
}

country_names = {
    "US": "United States of America", "BR": "Brazil", "DE": "Germany",
    "CN": "China", "IN": "India", "ZA": "South Africa", "AU": "Australia",
    "GB": "United Kingdom", "FR": "France", "JP": "Japan", "CA": "Canada",
    "MX": "Mexico", "AR": "Argentina", "RU": "Russia", "IT": "Italy",
    "ES": "Spain", "NL": "Netherlands", "KR": "South Korea", "NO": "Norway",
    "SE": "Sweden", "DK": "Denmark", "FI": "Finland"
}

# Currency mapping
country_currencies = {
    "BR": {"code": "BRL", "name": "Brazilian Real", "symbol": "R$"},
    "US": {"code": "USD", "name": "US Dollar", "symbol": "$"},
    "GB": {"code": "GBP", "name": "British Pound", "symbol": "£"},
    "DE": {"code": "EUR", "name": "Euro", "symbol": "€"},
    "FR": {"code": "EUR", "name": "Euro", "symbol": "€"},
    "IT": {"code": "EUR", "name": "Euro", "symbol": "€"},
    "ES": {"code": "EUR", "name": "Euro", "symbol": "€"},
    "NL": {"code": "EUR", "name": "Euro", "symbol": "€"},
    "JP": {"code": "JPY", "name": "Japanese Yen", "symbol": "¥"},
    "CN": {"code": "CNY", "name": "Chinese Yuan", "symbol": "¥"},
    "CA": {"code": "CAD", "name": "Canadian Dollar", "symbol": "C$"},
    "AU": {"code": "AUD", "name": "Australian Dollar", "symbol": "A$"},
    "IN": {"code": "INR", "name": "Indian Rupee", "symbol": "₹"},
    "KR": {"code": "KRW", "name": "South Korean Won", "symbol": "₩"},
    "MX": {"code": "MXN", "name": "Mexican Peso", "symbol": "$"},
    "AR": {"code": "ARS", "name": "Argentine Peso", "symbol": "$"},
    "RU": {"code": "RUB", "name": "Russian Ruble", "symbol": "₽"},
    "SE": {"code": "SEK", "name": "Swedish Krona", "symbol": "kr"}
}

# Timezone mapping
country_timezones_map = {
    "BR": "America/Sao_Paulo", "US": "America/New_York", "CA": "America/Toronto",
    "MX": "America/Mexico_City", "AR": "America/Argentina/Buenos_Aires",
    "CL": "America/Santiago", "GB": "Europe/London", "DE": "Europe/Berlin",
    "FR": "Europe/Paris", "IT": "Europe/Rome", "ES": "Europe/Madrid",
    "NL": "Europe/Amsterdam", "CN": "Asia/Shanghai", "JP": "Asia/Tokyo",
    "IN": "Asia/Kolkata", "AU": "Australia/Sydney", "KR": "Asia/Seoul",
    "NO": "Europe/Oslo", "SE": "Europe/Stockholm", "DK": "Europe/Copenhagen",
    "RU": "Europe/Moscow"
}

# Multi-language support
TRANSLATIONS = {
    'en': {
        'title': 'NetScan Pro - Advanced Network Intelligence Platform',
        'subtitle': 'Advanced Network Intelligence & Threat Analysis Platform',
        'search_placeholder': 'Enter IP address for comprehensive network intelligence analysis...',
        'analyze_btn': 'Analyze Network',
        'basic_info': 'Basic Information',
        'geographic_intel': 'Geographic Intelligence',
        'time_intel': 'Time Intelligence',
        'network_intel': 'Network Intelligence',
        'security_intel': 'Security & Threat Intelligence',
        'performance_analysis': 'Performance Analysis',
        'weather_info': 'Weather Information',
        'currency_info': 'Currency Information',
        'country': 'Country',
        'city': 'City',
        'timezone': 'Timezone',
        'risk_score': 'Risk Score',
        'export_report': 'Export Report',
        'login': 'Login',
        'register': 'Register',
        'dashboard': 'Dashboard',
        'bulk_analysis': 'Bulk Analysis',
        'history': 'History'
    },
    'pt': {
        'title': 'NetScan Pro - Plataforma Avançada de Inteligência de Rede',
        'subtitle': 'Plataforma Avançada de Inteligência de Rede e Análise de Ameaças',
        'search_placeholder': 'Digite o endereço IP para análise abrangente de inteligência de rede...',
        'analyze_btn': 'Analisar Rede',
        'basic_info': 'Informações Básicas',
        'geographic_intel': 'Inteligência Geográfica',
        'time_intel': 'Inteligência Temporal',
        'network_intel': 'Inteligência de Rede',
        'security_intel': 'Inteligência de Segurança e Ameaças',
        'performance_analysis': 'Análise de Performance',
        'weather_info': 'Informações Meteorológicas',
        'currency_info': 'Informações de Moeda',
        'country': 'País',
        'city': 'Cidade',
        'timezone': 'Fuso Horário',
        'risk_score': 'Pontuação de Risco',
        'export_report': 'Exportar Relatório',
        'login': 'Entrar',
        'register': 'Registrar',
        'dashboard': 'Painel',
        'bulk_analysis': 'Análise em Lote',
        'history': 'Histórico'
    },
    'es': {
        'title': 'NetScan Pro - Plataforma Avanzada de Inteligencia de Red',
        'subtitle': 'Plataforma Avanzada de Inteligencia de Red y Análisis de Amenazas',
        'search_placeholder': 'Ingrese la dirección IP para análisis integral de inteligencia de red...',
        'analyze_btn': 'Analizar Red',
        'basic_info': 'Información Básica',
        'geographic_intel': 'Inteligencia Geográfica',
        'time_intel': 'Inteligencia Temporal',
        'network_intel': 'Inteligencia de Red',
        'security_intel': 'Inteligencia de Seguridad y Amenazas',
        'performance_analysis': 'Análisis de Rendimiento',
        'weather_info': 'Información Meteorológica',
        'currency_info': 'Información de Moneda',
        'country': 'País',
        'city': 'Ciudad',
        'timezone': 'Zona Horaria',
        'risk_score': 'Puntuación de Riesgo',
        'export_report': 'Exportar Informe',
        'login': 'Iniciar Sesión',
        'register': 'Registrarse',
        'dashboard': 'Panel',
        'bulk_analysis': 'Análisis en Lote',
        'history': 'Historial'
    },
    'fr': {
        'title': 'NetScan Pro - Plateforme Avancée d\'Intelligence Réseau',
        'subtitle': 'Plateforme Avancée d\'Intelligence Réseau et d\'Analyse des Menaces',
        'search_placeholder': 'Entrez l\'adresse IP pour une analyse complète de l\'intelligence réseau...',
        'analyze_btn': 'Analyser le Réseau',
        'basic_info': 'Informations de Base',
        'geographic_intel': 'Intelligence Géographique',
        'time_intel': 'Intelligence Temporelle',
        'network_intel': 'Intelligence Réseau',
        'security_intel': 'Intelligence de Sécurité et Menaces',
        'performance_analysis': 'Analyse de Performance',
        'weather_info': 'Informations Météorologiques',
        'currency_info': 'Informations Monétaires',
        'country': 'Pays',
        'city': 'Ville',
        'timezone': 'Fuseau Horaire',
        'risk_score': 'Score de Risque',
        'export_report': 'Exporter le Rapport',
        'login': 'Connexion',
        'register': 'S\'inscrire',
        'dashboard': 'Tableau de Bord',
        'bulk_analysis': 'Analyse en Lot',
        'history': 'Historique'
    },
    'de': {
        'title': 'NetScan Pro - Erweiterte Netzwerk-Intelligence-Plattform',
        'subtitle': 'Erweiterte Netzwerk-Intelligence und Bedrohungsanalyse-Plattform',
        'search_placeholder': 'IP-Adresse für umfassende Netzwerk-Intelligence-Analyse eingeben...',
        'analyze_btn': 'Netzwerk Analysieren',
        'basic_info': 'Grundinformationen',
        'geographic_intel': 'Geografische Intelligence',
        'time_intel': 'Zeit-Intelligence',
        'network_intel': 'Netzwerk-Intelligence',
        'security_intel': 'Sicherheits- und Bedrohungs-Intelligence',
        'performance_analysis': 'Leistungsanalyse',
        'weather_info': 'Wetterinformationen',
        'currency_info': 'Währungsinformationen',
        'country': 'Land',
        'city': 'Stadt',
        'timezone': 'Zeitzone',
        'risk_score': 'Risiko-Score',
        'export_report': 'Bericht Exportieren',
        'login': 'Anmelden',
        'register': 'Registrieren',
        'dashboard': 'Dashboard',
        'bulk_analysis': 'Massenanalyse',
        'history': 'Verlauf'
    },
    'ja': {
        'title': 'NetScan Pro - 高度なネットワークインテリジェンスプラットフォーム',
        'subtitle': '高度なネットワークインテリジェンスと脅威分析プラットフォーム',
        'search_placeholder': '包括的なネットワークインテリジェンス分析のためのIPアドレスを入力...',
        'analyze_btn': 'ネットワーク分析',
        'basic_info': '基本情報',
        'geographic_intel': '地理的インテリジェンス',
        'time_intel': '時間インテリジェンス',
        'network_intel': 'ネットワークインテリジェンス',
        'security_intel': 'セキュリティ・脅威インテリジェンス',
        'performance_analysis': 'パフォーマンス分析',
        'weather_info': '天気情報',
        'currency_info': '通貨情報',
        'country': '国',
        'city': '都市',
        'timezone': 'タイムゾーン',
        'risk_score': 'リスクスコア',
        'export_report': 'レポートエクスポート',
        'login': 'ログイン',
        'register': '登録',
        'dashboard': 'ダッシュボード',
        'bulk_analysis': 'バルク分析',
        'history': '履歴'
    },
    'ko': {
        'title': 'NetScan Pro - 고급 네트워크 인텔리전스 플랫폼',
        'subtitle': '고급 네트워크 인텔리전스 및 위협 분석 플랫폼',
        'search_placeholder': '포괄적인 네트워크 인텔리전스 분석을 위한 IP 주소 입력...',
        'analyze_btn': '네트워크 분석',
        'basic_info': '기본 정보',
        'geographic_intel': '지리적 인텔리전스',
        'time_intel': '시간 인텔리전스',
        'network_intel': '네트워크 인텔리전스',
        'security_intel': '보안 및 위협 인텔리전스',
        'performance_analysis': '성능 분석',
        'weather_info': '날씨 정보',
        'currency_info': '통화 정보',
        'country': '국가',
        'city': '도시',
        'timezone': '시간대',
        'risk_score': '위험 점수',
        'export_report': '보고서 내보내기',
        'login': '로그인',
        'register': '등록',
        'dashboard': '대시보드',
        'bulk_analysis': '대량 분석',
        'history': '기록'
    },
    'zh': {
        'title': 'NetScan Pro - 高级网络情报平台',
        'subtitle': '高级网络情报和威胁分析平台',
        'search_placeholder': '输入IP地址进行全面网络情报分析...',
        'analyze_btn': '分析网络',
        'basic_info': '基本信息',
        'geographic_intel': '地理情报',
        'time_intel': '时间情报',
        'network_intel': '网络情报',
        'security_intel': '安全和威胁情报',
        'performance_analysis': '性能分析',
        'weather_info': '天气信息',
        'currency_info': '货币信息',
        'country': '国家',
        'city': '城市',
        'timezone': '时区',
        'risk_score': '风险评分',
        'export_report': '导出报告',
        'login': '登录',
        'register': '注册',
        'dashboard': '仪表板',
        'bulk_analysis': '批量分析',
        'history': '历史'
    },
    'sv': {
        'title': 'NetScan Pro - Avancerad Nätverksintelligensplattform',
        'subtitle': 'Avancerad Nätverksintelligens och Hotanalysplattform',
        'search_placeholder': 'Ange IP-adress för omfattande nätverksintelligensanalys...',
        'analyze_btn': 'Analysera Nätverk',
        'basic_info': 'Grundläggande Information',
        'geographic_intel': 'Geografisk Intelligens',
        'time_intel': 'Tidsintelligens',
        'network_intel': 'Nätverksintelligens',
        'security_intel': 'Säkerhets- och Hotintelligens',
        'performance_analysis': 'Prestandaanalys',
        'weather_info': 'Väderinformation',
        'currency_info': 'Valutainformation',
        'country': 'Land',
        'city': 'Stad',
        'timezone': 'Tidszon',
        'risk_score': 'Riskpoäng',
        'export_report': 'Exportera Rapport',
        'login': 'Logga In',
        'register': 'Registrera',
        'dashboard': 'Instrumentpanel',
        'bulk_analysis': 'Massanalys',
        'history': 'Historik'
    },
    'ru': {
        'title': 'NetScan Pro - Продвинутая Платформа Сетевой Разведки',
        'subtitle': 'Продвинутая Платформа Сетевой Разведки и Анализа Угроз',
        'search_placeholder': 'Введите IP-адрес для комплексного анализа сетевой разведки...',
        'analyze_btn': 'Анализировать Сеть',
        'basic_info': 'Основная Информация',
        'geographic_intel': 'Географическая Разведка',
        'time_intel': 'Временная Разведка',
        'network_intel': 'Сетевая Разведка',
        'security_intel': 'Разведка Безопасности и Угроз',
        'performance_analysis': 'Анализ Производительности',
        'weather_info': 'Информация о Погоде',
        'currency_info': 'Информация о Валюте',
        'country': 'Страна',
        'city': 'Город',
        'timezone': 'Часовой Пояс',
        'risk_score': 'Оценка Риска',
        'export_report': 'Экспорт Отчета',
        'login': 'Вход',
        'register': 'Регистрация',
        'dashboard': 'Панель',
        'bulk_analysis': 'Массовый Анализ',
        'history': 'История'
    },
    'nl': {
        'title': 'NetScan Pro - Geavanceerd Netwerk Intelligence Platform',
        'subtitle': 'Geavanceerd Netwerk Intelligence en Dreigingsanalyse Platform',
        'search_placeholder': 'Voer IP-adres in voor uitgebreide netwerk intelligence analyse...',
        'analyze_btn': 'Netwerk Analyseren',
        'basic_info': 'Basisinformatie',
        'geographic_intel': 'Geografische Intelligence',
        'time_intel': 'Tijd Intelligence',
        'network_intel': 'Netwerk Intelligence',
        'security_intel': 'Beveiligings- en Dreigingsintelligence',
        'performance_analysis': 'Prestatie-analyse',
        'weather_info': 'Weerinformatie',
        'currency_info': 'Valuta-informatie',
        'country': 'Land',
        'city': 'Stad',
        'timezone': 'Tijdzone',
        'risk_score': 'Risicoscore',
        'export_report': 'Rapport Exporteren',
        'login': 'Inloggen',
        'register': 'Registreren',
        'dashboard': 'Dashboard',
        'bulk_analysis': 'Bulk Analyse',
        'history': 'Geschiedenis'
    },
    'hi': {
        'title': 'NetScan Pro - उन्नत नेटवर्क इंटेलिजेंस प्लेटफ़ॉर्म',
        'subtitle': 'उन्नत नेटवर्क इंटेलिजेंस और खतरा विश्लेषण प्लेटफ़ॉर्म',
        'search_placeholder': 'व्यापक नेटवर्क इंटेलिजेंस विश्लेषण के लिए IP पता दर्ज करें...',
        'analyze_btn': 'नेटवर्क का विश्लेषण करें',
        'basic_info': 'बुनियादी जानकारी',
        'geographic_intel': 'भौगोलिक इंटेलिजेंस',
        'time_intel': 'समय इंटेलिजेंस',
        'network_intel': 'नेटवर्क इंटेलिजेंस',
        'security_intel': 'सुरक्षा और खतरा इंटेलिजेंस',
        'performance_analysis': 'प्रदर्शन विश्लेषण',
        'weather_info': 'मौसम की जानकारी',
        'currency_info': 'मुद्रा की जानकारी',
        'country': 'देश',
        'city': 'शहर',
        'timezone': 'समय क्षेत्र',
        'risk_score': 'जोखिम स्कोर',
        'export_report': 'रिपोर्ट निर्यात करें',
        'login': 'लॉगिन',
        'register': 'पंजीकरण',
        'dashboard': 'डैशबोर्ड',
        'bulk_analysis': 'बल्क विश्लेषण',
        'history': 'इतिहास'
    }
}

# Global cache for better performance
@lru_cache(maxsize=1000)
def cached_request(url, timeout=10):
    try:
        response = requests.get(url, timeout=timeout)
        return response.json() if response.status_code == 200 else None
    except:
        return None

# Enhanced detection functions
def detect_usage_type(asn_description, org_name, isp_name):
    text = f"{asn_description or ''} {org_name or ''} {isp_name or ''}".lower()
    
    if any(keyword in text for keyword in ['google', 'amazon', 'microsoft', 'cloudflare', 'digital ocean', 'linode', 'vultr']):
        return "DCH"  # Data Center/Hosting
    elif any(keyword in text for keyword in ['mobile', 'cellular', 'wireless', 'gsm', 'lte', 'vivo', 'claro', 'tim', 'oi', 'vodafone', 'at&t', 'verizon']):
        return "MOB"  # Mobile
    elif any(keyword in text for keyword in ['university', 'education', 'school', 'college', 'academic']):
        return "EDU"  # Educational
    elif any(keyword in text for keyword in ['government', 'military', 'gov', 'defense']):
        return "GOV"  # Government
    elif any(keyword in text for keyword in ['business', 'enterprise', 'corporate']):
        return "COM"  # Commercial
    else:
        return "ISP"  # Internet Service Provider

def reverse_dns(ip):
    try:
        result = socket.gethostbyaddr(ip)[0]
        return result
    except:
        return None

# Enhanced geolocation with multiple sources
def get_comprehensive_geo_data(ip):
    print(f"🌍 Getting comprehensive geo data for {ip}")
    geo_sources = []
    
    # Source 1: ip-api.com (most comprehensive)
    try:
        url = f"http://ip-api.com/json/{ip}?fields=status,continent,continentCode,country,countryCode,region,regionName,city,district,zip,lat,lon,timezone,offset,currency,isp,org,as,asname,mobile,proxy,hosting,query"
        data = cached_request(url)
        if data and data.get("status") == "success":
            geo_sources.append(("ip-api.com", data))
    except Exception as e:
        print(f"Error with ip-api.com: {e}")
    
    # Source 2: ipapi.co
    try:
        url = f"http://ipapi.co/{ip}/json/"
        data = cached_request(url)
        if data and 'error' not in data:
            geo_sources.append(("ipapi.co", data))
    except Exception as e:
        print(f"Error with ipapi.co: {e}")
    
    # Source 3: ipinfo.io (free tier)
    try:
        url = f"http://ipinfo.io/{ip}/json"
        data = cached_request(url)
        if data and 'bogon' not in data:
            geo_sources.append(("ipinfo.io", data))
    except Exception as e:
        print(f"Error with ipinfo.io: {e}")
    
    return geo_sources

# Weather data integration
def get_real_weather_data(lat, lon):
    try:
        if OPENWEATHER_API_KEY and OPENWEATHER_API_KEY != "your_openweather_api_key_here":
            url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
            data = cached_request(url)
            
            if data:
                return {
                    "temperature": f"{data['main']['temp']}°C",
                    "description": data['weather'][0]['description'].title(),
                    "humidity": f"{data['main']['humidity']}%",
                    "pressure": f"{data['main']['pressure']} hPa",
                    "wind_speed": f"{data.get('wind', {}).get('speed', 0)} m/s",
                    "available": True
                }
    except Exception as e:
        print(f"Weather API error: {e}")
    
    return {
        "temperature": "N/A",
        "description": "Weather data unavailable",
        "humidity": "N/A",
        "available": False
    }

# Enhanced WHOIS with more details
def get_enhanced_whois_data(ip):
    try:
        print(f"🔍 Enhanced WHOIS lookup for {ip}")
        obj = IPWhois(ip)
        res = obj.lookup_rdap(depth=2)
        
        network = res.get("network", {})
        
        return {
            "asn": res.get("asn"),
            "asn_description": res.get("asn_description"),
            "asn_country_code": res.get("asn_country_code"),
            "asn_date": res.get("asn_date"),
            "asn_registry": res.get("asn_registry"),
            "network_name": network.get("name"),
            "network_handle": network.get("handle"),
            "network_status": network.get("status"),
            "network_type": network.get("type"),
            "network_country": network.get("country"),
            "network_start_address": network.get("start_address"),
            "network_end_address": network.get("end_address"),
            "network_cidr": network.get("cidr"),
            "network_parent_handle": network.get("parent_handle")
        }
    except Exception as e:
        print(f"Enhanced WHOIS error: {e}")
        return {}

# Security threat analysis
def analyze_security_threats(ip, domain, org, asn_desc):
    threats = {
        "risk_score": 0,
        "threat_types": [],
        "reputation": "Unknown",
        "is_malicious": False,
        "last_seen": None
    }
    
    # Basic threat analysis
    text = f"{domain or ''} {org or ''} {asn_desc or ''}".lower()
    
    # Check for known patterns
    if any(keyword in text for keyword in ['tor', 'proxy', 'vpn']):
        threats["risk_score"] += 20
        threats["threat_types"].append("Anonymization Service")
    
    if any(keyword in text for keyword in ['botnet', 'malware', 'spam']):
        threats["risk_score"] += 40
        threats["threat_types"].append("Malicious Activity")
    
    if any(keyword in text for keyword in ['datacenter', 'hosting', 'cloud']):
        threats["risk_score"] += 10
        threats["threat_types"].append("Hosting Provider")
    
    # Set reputation based on score
    if threats["risk_score"] <= 10:
        threats["reputation"] = "Good"
    elif threats["risk_score"] <= 30:
        threats["reputation"] = "Suspicious"
    else:
        threats["reputation"] = "High Risk"
    
    threats["is_malicious"] = threats["risk_score"] > 50
    
    return threats

# Network performance analysis
def analyze_network_performance(ip, country_code, org):
    performance = {
        "estimated_speed": "Unknown",
        "connection_type": "Unknown",
        "quality_score": 0,
        "latency_estimate": "Unknown"
    }
    
    text = f"{org or ''}".lower()
    
    # Estimate based on provider
    if any(keyword in text for keyword in ['google', 'cloudflare', 'amazon', 'microsoft']):
        performance["estimated_speed"] = "Very High (1Gbps+)"
        performance["connection_type"] = "Fiber/Data Center"
        performance["quality_score"] = 95
        performance["latency_estimate"] = "< 10ms"
    elif any(keyword in text for keyword in ['fiber', 'broadband']):
        performance["estimated_speed"] = "High (100-1000Mbps)"
        performance["connection_type"] = "Fiber Broadband"
        performance["quality_score"] = 85
        performance["latency_estimate"] = "10-30ms"
    elif any(keyword in text for keyword in ['mobile', 'cellular', 'lte', '5g']):
        performance["estimated_speed"] = "Medium (10-100Mbps)"
        performance["connection_type"] = "Mobile/Cellular"
        performance["quality_score"] = 70
        performance["latency_estimate"] = "30-100ms"
    else:
        performance["estimated_speed"] = "Standard (1-50Mbps)"
        performance["connection_type"] = "Broadband"
        performance["quality_score"] = 60
        performance["latency_estimate"] = "20-80ms"
    
    return performance

# Bulk analysis function
def analyze_multiple_ips(ip_list):
    results = []
    for ip in ip_list:
        try:
            analysis = comprehensive_ip_analysis(ip.strip())
            results.append(analysis)
        except Exception as e:
            results.append({"ip": ip, "error": str(e)})
    return results

# Main enhanced IP analysis function
@monitor_performance
def comprehensive_ip_analysis(ip):
    print(f"\n🚀 COMPREHENSIVE ANALYSIS STARTING FOR: {ip}")
    start_time = time.time()
    
    # Initialize comprehensive data structure
    analysis = {
        "ip": ip,
        "analysis_timestamp": dt.utcnow().isoformat() + "Z",
        "analysis_duration": 0,
        
        # Basic info
        "basic": {
            "ip_type": None,
            "reverse_dns": None,
            "domain": None,
            "ptr_record": None
        },
        
        # Geographic intelligence
        "geographic": {
            "country_code": None,
            "country_name": None,
            "continent": None,
            "continent_code": None,
            "region": None,
            "city": None,
            "district": None,
            "postal_code": None,
            "coordinates": {"lat": None, "lon": None},
            "accuracy_radius": None
        },
        
        # Time intelligence
        "time": {
            "timezone": None,
            "utc_offset": None,
            "utc_offset_formatted": None,
            "local_time": None,
            "utc_time": None,
            "is_dst": None,
            "dst_offset": None
        },
        
        # Currency info
        "currency": {
            "code": None,
            "name": None,
            "symbol": None
        },
        
        # Weather info
        "weather": {"available": False},
        
        # Network intelligence
        "network": {
            "asn": None,
            "asn_description": None,
            "asn_country": None,
            "asn_registry": None,
            "organization": None,
            "isp": None,
            "network_name": None,
            "cidr": None,
            "network_type": None,
            "usage_type": None,
            "is_mobile": False,
            "is_proxy": False,
            "is_hosting": False,
            "is_datacenter": False
        },
        
        # Security analysis
        "security": {
            "threat_analysis": {},
            "is_tor": False,
            "is_vpn": False,
            "is_malicious": False,
            "reputation_score": 0,
            "threat_types": [],
            "blacklist_status": []
        },
        
        # Performance analysis
        "performance": {},
        
        # Raw data sources
        "sources": {
            "whois": {},
            "geolocation": []
        }
    }
    
    # Basic analysis
    print("📍 Basic analysis...")
    try:
        ip_obj = ipaddress.ip_address(ip)
        if ip_obj.is_private:
            analysis["basic"]["ip_type"] = "Private"
        elif ip_obj.is_loopback:
            analysis["basic"]["ip_type"] = "Loopback"
        elif ip_obj.is_multicast:
            analysis["basic"]["ip_type"] = "Multicast"
        elif ip_obj.is_reserved:
            analysis["basic"]["ip_type"] = "Reserved"
        else:
            analysis["basic"]["ip_type"] = "Public"
    except:
        analysis["basic"]["ip_type"] = "Invalid"
    
    # Reverse DNS
    analysis["basic"]["reverse_dns"] = reverse_dns(ip)
    if analysis["basic"]["reverse_dns"]:
        parts = analysis["basic"]["reverse_dns"].split('.')
        if len(parts) >= 2:
            analysis["basic"]["domain"] = '.'.join(parts[-2:])
    
    # Enhanced WHOIS
    print("🔍 Enhanced WHOIS analysis...")
    whois_data = get_enhanced_whois_data(ip)
    analysis["sources"]["whois"] = whois_data
    
    if whois_data:
        analysis["network"].update({
            "asn": whois_data.get("asn"),
            "asn_description": whois_data.get("asn_description"),
            "asn_country": whois_data.get("asn_country_code"),
            "asn_registry": whois_data.get("asn_registry"),
            "organization": whois_data.get("network_name"),
            "network_name": whois_data.get("network_name"),
            "cidr": whois_data.get("network_cidr"),
            "network_type": whois_data.get("network_type")
        })
    
    # Comprehensive geolocation
    print("🌍 Comprehensive geolocation...")
    geo_sources = get_comprehensive_geo_data(ip)
    analysis["sources"]["geolocation"] = geo_sources
    
    # Process geolocation data with priority
    for source_name, geo_data in geo_sources:
        print(f"📊 Processing {source_name} data...")
        
        if source_name == "ip-api.com":
            analysis["geographic"].update({
                "country_code": geo_data.get("countryCode") or analysis["geographic"]["country_code"],
                "country_name": geo_data.get("country") or analysis["geographic"]["country_name"],
                "continent": geo_data.get("continent") or analysis["geographic"]["continent"],
                "continent_code": geo_data.get("continentCode") or analysis["geographic"]["continent_code"],
                "region": geo_data.get("regionName") or analysis["geographic"]["region"],
                "city": geo_data.get("city") or analysis["geographic"]["city"],
                "district": geo_data.get("district") or analysis["geographic"]["district"],
                "postal_code": geo_data.get("zip") or analysis["geographic"]["postal_code"],
                "coordinates": {
                    "lat": geo_data.get("lat") or analysis["geographic"]["coordinates"]["lat"],
                    "lon": geo_data.get("lon") or analysis["geographic"]["coordinates"]["lon"]
                }
            })
            
            analysis["time"].update({
                "timezone": geo_data.get("timezone") or analysis["time"]["timezone"],
                "utc_offset": geo_data.get("offset") or analysis["time"]["utc_offset"]
            })
            
            analysis["network"].update({
                "isp": geo_data.get("isp") or analysis["network"]["isp"],
                "organization": geo_data.get("org") or analysis["network"]["organization"],
                "asn": geo_data.get("as", "").split()[0].replace("AS", "") if geo_data.get("as") else analysis["network"]["asn"],
                "is_mobile": geo_data.get("mobile", False),
                "is_proxy": geo_data.get("proxy", False),
                "is_hosting": geo_data.get("hosting", False)
            })
        
        elif source_name == "ipapi.co":
            analysis["geographic"].update({
                "country_code": analysis["geographic"]["country_code"] or geo_data.get("country_code"),
                "country_name": analysis["geographic"]["country_name"] or geo_data.get("country_name"),
                "region": analysis["geographic"]["region"] or geo_data.get("region"),
                "city": analysis["geographic"]["city"] or geo_data.get("city"),
                "postal_code": analysis["geographic"]["postal_code"] or geo_data.get("postal"),
                "coordinates": {
                    "lat": analysis["geographic"]["coordinates"]["lat"] or geo_data.get("latitude"),
                    "lon": analysis["geographic"]["coordinates"]["lon"] or geo_data.get("longitude")
                }
            })
            
            analysis["time"]["timezone"] = analysis["time"]["timezone"] or geo_data.get("timezone")
            analysis["network"]["organization"] = analysis["network"]["organization"] or geo_data.get("org")
    
    # Fallback data enrichment
    print("🔧 Data enrichment and fallbacks...")
    
    # Country name fallback
    if analysis["geographic"]["country_code"] and not analysis["geographic"]["country_name"]:
        analysis["geographic"]["country_name"] = country_names.get(
            analysis["geographic"]["country_code"], 
            f"Country {analysis['geographic']['country_code']}"
        )
    
    # Continent fallback
    if analysis["geographic"]["country_code"] and not analysis["geographic"]["continent"]:
        analysis["geographic"]["continent"] = continent_map.get(analysis["geographic"]["country_code"])
    
    # Timezone fallback
    if analysis["geographic"]["country_code"] and not analysis["time"]["timezone"]:
        analysis["time"]["timezone"] = country_timezones_map.get(analysis["geographic"]["country_code"])
    
    # Currency information
    if analysis["geographic"]["country_code"]:
        currency_info = country_currencies.get(analysis["geographic"]["country_code"])
        if currency_info:
            analysis["currency"] = currency_info
    
    # Time processing
    if analysis["time"]["timezone"]:
        try:
            tz = timezone(analysis["time"]["timezone"])
            local_time = dt.now(tz)
            utc_time = dt.utcnow()
            
            analysis["time"].update({
                "local_time": local_time.strftime("%Y-%m-%d %H:%M:%S %Z"),
                "utc_time": utc_time.strftime("%Y-%m-%d %H:%M:%S UTC"),
                "is_dst": bool(local_time.dst()),
                "utc_offset": int(local_time.utcoffset().total_seconds()) if local_time.utcoffset() else 0
            })
            
            # Format UTC offset nicely
            offset_hours = analysis["time"]["utc_offset"] // 3600
            analysis["time"]["utc_offset_formatted"] = f"UTC{offset_hours:+d}" if offset_hours != 0 else "UTC"
            
        except Exception as e:
            print(f"Time processing error: {e}")
    
    # Weather information (if coordinates available)
    if analysis["geographic"]["coordinates"]["lat"] and analysis["geographic"]["coordinates"]["lon"]:
        print("🌤️ Getting weather data...")
        analysis["weather"] = get_real_weather_data(
            analysis["geographic"]["coordinates"]["lat"],
            analysis["geographic"]["coordinates"]["lon"]
        )
    
    # Network analysis
    analysis["network"]["usage_type"] = detect_usage_type(
        analysis["network"]["asn_description"],
        analysis["network"]["organization"],
        analysis["network"]["isp"]
    )
    
    # Datacenter detection
    text = f"{analysis['basic']['domain'] or ''} {analysis['network']['organization'] or ''} {analysis['network']['asn_description'] or ''}".lower()
    analysis["network"]["is_datacenter"] = any(keyword in text for keyword in [
        'amazon', 'aws', 'google', 'microsoft', 'azure', 'digitalocean',
        'linode', 'vultr', 'ovh', 'hetzner', 'cloudflare', 'fastly',
        'hosting', 'datacenter', 'data center', 'cloud', 'server'
    ])
    
    # Security analysis
    print("🔒 Security analysis...")
    analysis["security"]["threat_analysis"] = analyze_security_threats(
        ip, 
        analysis["basic"]["domain"],
        analysis["network"]["organization"],
        analysis["network"]["asn_description"]
    )
    
    # Tor check
    try:
        response = requests.get("https://check.torproject.org/exit-addresses", timeout=5)
        if response.status_code == 200:
            analysis["security"]["is_tor"] = ip in response.text
    except:
        pass
    
    # Performance analysis
    print("⚡ Performance analysis...")
    analysis["performance"] = analyze_network_performance(
        ip,
        analysis["geographic"]["country_code"],
        analysis["network"]["organization"]
    )
    
    # Final statistics
    analysis["analysis_duration"] = round(time.time() - start_time, 2)
    
    print(f"✅ Analysis completed in {analysis['analysis_duration']} seconds")
    
    return analysis

# Flask routes
@app.route("/")
def index():
    lang = request.args.get('lang', 'en')
    if lang not in TRANSLATIONS:
        lang = 'en'
    
    # Track user visit for analytics (with improved error handling)
    session_id = None
    try:
        firebase_svc = get_firebase_service()
        if firebase_svc and firebase_svc.is_ready():
            session_id = firebase_svc.track_user_visit(request)
            if session_id:
                session['session_id'] = session_id
    except Exception as e:
        print(f"⚠️  Error tracking user visit: {e}")
    
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ip and ',' in ip:
        ip = ip.split(',')[0].strip()
    
    if not ip or ip.startswith("::") or ip == "127.0.0.1" or ip.startswith("192.168") or ip.startswith("10."):
        ip = "8.8.8.8"  # Test IP
    
    data = comprehensive_ip_analysis(ip)
    return render_template("index.html", data=data, lang=lang, translations=TRANSLATIONS[lang])

@app.route("/api/<ip>")
def api_endpoint(ip):
    """Enhanced API endpoint with comprehensive analysis"""
    try:
        # Validate IP input
        ip = validate_ip_input(ip)
        
        # Track scanning event with improved error handling
        try:
            firebase_svc = get_firebase_service()
            if firebase_svc and firebase_svc.is_ready():
                session_id = session.get('session_id')
                firebase_svc.track_scan_event(ip, 'api', session_id=session_id)
        except Exception as e:
            print(f"⚠️  Error tracking scan event: {e}")
        
        data = comprehensive_ip_analysis(ip)
        
        # Sanitize output for security
        sanitized_data = sanitize_output(data)
        
        return jsonify(sanitized_data)
    except ValueError as e:
        return jsonify({"error": f"Invalid input: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Admin route for user analytics (private)
@app.route("/admin/analytics")
def admin_analytics():
    """Private admin analytics endpoint"""
    try:
        admin_key = request.headers.get('X-Admin-Key') or request.args.get('admin_key')
        
        firebase_svc = get_firebase_service()
        if not firebase_svc:
            return jsonify({'error': 'Firebase service not initialized', 'code': 503}), 503
        
        stats = firebase_svc.get_user_stats(admin_key)
        
        if 'error' in stats:
            status_code = stats.get('code', 500)
            return jsonify(stats), status_code
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}', 'code': 500}), 500

# Admin dashboard route
@app.route("/admin/dashboard")
def admin_dashboard():
    """Private admin dashboard with enhanced error handling"""
    try:
        admin_key = request.headers.get('X-Admin-Key') or request.args.get('admin_key')
        
        firebase_svc = get_firebase_service()
        if not firebase_svc:
            return render_template("admin_error.html", 
                                 error="Firebase service not initialized", 
                                 details="The analytics system is not available.")
        
        stats = firebase_svc.get_user_stats(admin_key)
        
        if 'error' in stats:
            error_details = "Please check your admin key and Firebase configuration."
            if stats.get('code') == 401:
                error_details = "Invalid admin key provided."
            elif stats.get('code') == 503:
                error_details = "Firebase analytics service is not available."
            
            return render_template("admin_error.html", 
                                 error=stats['error'], 
                                 details=error_details)
        
        return render_template("admin_dashboard.html", stats=stats)
    except Exception as e:
        return render_template("admin_error.html", 
                             error=f"Dashboard error: {str(e)}", 
                             details="An unexpected error occurred while loading the dashboard.")

# Firebase health check endpoint
@app.route("/admin/health")
def firebase_health():
    """Firebase service health check"""
    try:
        admin_key = request.headers.get('X-Admin-Key') or request.args.get('admin_key')
        
        # Verify admin access
        from config import config
        env = os.environ.get('FLASK_ENV', 'development')
        app_config = config[env]
        admin_secret = getattr(app_config, 'ADMIN_SECRET_KEY', None)
        
        if not admin_secret or admin_key != admin_secret:
            return jsonify({'error': 'Unauthorized'}), 401
        
        firebase_svc = get_firebase_service()
        if not firebase_svc:
            return jsonify({
                'status': 'not_initialized',
                'firebase_service': False
            })
        
        health_status = firebase_svc.health_check()
        return jsonify(health_status)
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

# ...existing routes...

if __name__ == '__main__':
    print("🚀 Iniciando NetScan Pro...")
    print(f"🌍 Ambiente: {env}")
    print(f"🔒 Modo Debug: {app.config.get('DEBUG', False)}")
    print(f"🔥 Firebase habilitado: {firebase_service is not None}")
    print("📡 Servidor iniciando na porta 5000...")
    print("🌐 Acesse: http://localhost:5000")
    print("🔐 Dashboard Admin: http://localhost:5000/admin")
    print("-" * 50)
    
    # Iniciar o servidor Flask
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.config.get('DEBUG', False),
        threaded=True
    )