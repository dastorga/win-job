#!/usr/bin/env python3
"""
Demo LinkedIn API Service - Sin credenciales reales
Demostración del servicio usando datos de muestra
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from datetime import datetime
import logging
from app.services.linkedin_api_service import LinkedInAPIService

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

def print_header():
    """Print the script header"""
    print("🚀 LINKEDIN API - DEMO (SIN CREDENCIALES)")
    print("=" * 60)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🔗 Simulando LinkedIn API con datos de muestra")
    print()

def get_search_parameters():
    """Get search parameters from user"""
    print("🔍 PARÁMETROS DE BÚSQUEDA")
    print("-" * 40)
    
    keywords = input("💼 Palabras clave (default: DevOps): ").strip() or "DevOps"
    location = input("📍 Ubicación (default: Chile): ").strip() or "Chile"
    
    try:
        limit = int(input("🔢 Máximo trabajos (default: 10): ").strip() or "10")
    except ValueError:
        limit = 10
        
    return keywords, location, limit

def print_jobs_results(jobs):
    """Print job search results"""
    print("\n📊 RESULTADOS DE LA BÚSQUEDA API")
    print("=" * 60)
    print(f"   - Trabajos encontrados: {len(jobs)}")
    
    if jobs:
        print(f"   - Trabajos sin inglés: {len([j for j in jobs if not j.get('requires_english', False)])}")
        print()
        
        print("📋 Detalles de los trabajos:")
        print("-" * 80)
        
        for i, job in enumerate(jobs, 1):
            print(f"\n🏢 Trabajo {i}:")
            print(f"   📝 Título: {job['title']}")
            print(f"   🏪 Empresa: {job['company']}")
            print(f"   📍 Ubicación: {job['location']}")
            
            if job.get('salary_range'):
                print(f"   💰 Salario: {job['salary_range']}")
            
            print(f"   👔 Tipo: {job['employment_type']}")
            print(f"   📊 Nivel: {job['seniority_level']}")
            print(f"   🇬🇧 Inglés: {'Sí' if job.get('requires_english', False) else 'No'}")
            print(f"   🌐 URL: {job['linkedin_url']}")
            
            # Description preview
            desc = job['description'][:120]
            if len(job['description']) > 120:
                desc += "..."
            print(f"   📄 Descripción: {desc}")
    else:
        print("\n❌ No se encontraron trabajos")

def main():
    """Main function"""
    print_header()
    
    try:
        # Get search parameters
        keywords, location, limit = get_search_parameters()
        
        print(f"\n🔎 INICIANDO DEMO DE BÚSQUEDA")
        print("-" * 40)
        print(f"   🔍 Palabras clave: {keywords}")
        print(f"   📍 Ubicación: {location}")
        print(f"   📊 Límite: {limit}")
        
        print("\n⏳ Simulando conexión con LinkedIn API...")
        
        # Create service without credentials (will use sample data)
        service = LinkedInAPIService()
        
        # Search jobs (will return sample data since no credentials)
        jobs = service.search_jobs(keywords, location, limit)
        
        # Print results
        print_jobs_results(jobs)
        
        # Save to database
        if jobs:
            print(f"\n💾 Guardando {len(jobs)} trabajos en base de datos...")
            saved_count = service.save_jobs_to_database(jobs)
            print(f"✅ {saved_count} trabajos guardados correctamente")
        
        print("\n🎉 Demo completada!")
        print("\n💡 NOTA: Para usar datos reales de LinkedIn:")
        print("   1. Usa el script test_linkedin_api.py")
        print("   2. Proporciona credenciales válidas de LinkedIn")
        print("   3. La API requiere autenticación para acceso completo")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo cancelada por el usuario")
    except Exception as e:
        print(f"\n❌ Error en demo: {e}")
        logger.error(f"Demo error: {e}")

if __name__ == "__main__":
    main()