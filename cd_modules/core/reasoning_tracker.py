class ReasoningTracker:
    """
    Rastreador de razonamiento deliberativo: guarda los pasos y calcula la métrica EEE.
    """

    def __init__(self):
        self.steps = []

    def add_step(self, question, sources, generated_answer):
        self.steps.append({
            "question": question,
            "sources": sources,
            "generated_answer": generated_answer
        })

    def get_steps(self):
        return self.steps

    def compute_eee(self):
        """
        Calcula la métrica Erotetic Equilibrium Evaluator (EEE).
        Por ahora: % de respuestas que usan al menos una fuente.
        """
        if not self.steps:
            return 0.0
        count_with_sources = sum(1 for step in self.steps if step["sources"])
        return round(100.0 * count_with_sources / len(self.steps), 2)
