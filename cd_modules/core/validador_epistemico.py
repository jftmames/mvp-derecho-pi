import os
from cd_modules.core.validador_epistemico import EroteticEvaluator

# os.environ["OPENAI_API_KEY"] = "sk-..."

def run_test_auditor():
    print("🚀 INICIANDO TEST DEL SPRINT 3: EL AUDITOR H-ANCHOR")
    
    auditor = EroteticEvaluator()
    
    # SIMULACIÓN DE CONTEXTO REAL (Lo que recuperó el RAGA del AI Act)
    evidencia_real = """
    (Fuente: Art. 5 AI Act)
    Se prohíben las prácticas de IA que utilicen técnicas subliminales que alteren 
    el comportamiento de una persona de manera que le cause perjuicio físico o psicológico.
    """
    
    print(f"\n📄 EVIDENCIA (RAGA): {evidencia_real.strip()}")
    
    # CASO 1: AFIRMACIÓN FALSA (ALUCINACIÓN)
    mentira = "El Artículo 5 permite técnicas subliminales si son para fines de marketing."
    print(f"\n🔹 Auditando Afirmación 1 (Falsa): '{mentira}'")
    
    resultado1 = auditor.audit_claim(mentira, evidencia_real)
    print(f"   👉 JUICIO: {resultado1['status'].upper()}")
    print(f"   📝 RAZÓN: {resultado1['reason']}")

    # CASO 2: AFIRMACIÓN VERDADERA
    verdad = "El uso de técnicas subliminales está prohibido si causa daño psicológico."
    print(f"\n🔹 Auditando Afirmación 2 (Verdadera): '{verdad}'")
    
    resultado2 = auditor.audit_claim(verdad, evidencia_real)
    print(f"   👉 JUICIO: {resultado2['status'].upper()}")
    print(f"   📝 RAZÓN: {resultado2['reason']}")

    # VERIFICACIÓN DEL HITO
    if resultado1['status'] == "no validada" and resultado2['status'] == "validada":
        print("\n✅ HITO CONSEGUIDO: El auditor distingue verdad de mentira basándose en la evidencia.")
    else:
        print("\n❌ FALLO: El auditor no juzgó correctamente.")

if __name__ == "__main__":
    run_test_auditor()
