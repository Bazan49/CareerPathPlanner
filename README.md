# Planificación Inteligente de Trayectorias Profesionales

Sistema de planificación automática de trayectorias profesionales basado en Inteligencia Artificial.

El sistema transforma objetivos profesionales expresados en lenguaje natural en una secuencia óptima de cursos utilizando técnicas de planificación automática basadas en STRIPS y algoritmos de búsqueda heurística. Además, incorpora simulación Monte Carlo para estimar la viabilidad real de las trayectorias generadas y modelos de lenguaje (LLM) para interpretar los objetivos del usuario y evaluar cualitativamente los resultados obtenidos.

## 🔧 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/Bazan49/CareerPathPlanner.git
cd CareerPathPlanner
```

### 2. Crear un entorno virtual

```bash
python -m venv .venv
```

### 3. Activar el entorno virtual

**Windows**

```bash
.venv\Scripts\activate
```

**Linux / macOS**

```bash
source .venv/bin/activate
```

### 4. Instalar las dependencias

```bash
pip install -r requirements.txt
```

## 🤖 Configuración del LLM

Para el correcto funcionamiento de las funcionalidades basadas en modelos de lenguaje (LLM), es necesario configurar una clave de acceso a la API de Mistral AI.

Obtenga una clave gratuita en https://console.mistral.ai y cree un archivo `.env` en la raíz del proyecto con el siguiente contenido:

```env
LLM_API_KEY=api_key
```

Sustituya `api_key` por la clave obtenida en Mistral AI.

## ▶️ Ejecución

El proyecto incluye un dataset sintético para el dominio de **Ciencia de Datos**, compuesto por un conjunto de habilidades (`skills.json`) y un catálogo de cursos (`courses.json`) con sus respectivos prerrequisitos y metadatos.

### Crear un experimento

```bash
python scripts/create_experiment.py
```

Durante la ejecución se solicitarán los siguientes parámetros:

- Nombre del experimento.
- Objetivo profesional del usuario.
- Ruta del dataset.
- Planificador a utilizar (`ucs`, `a_star_basic` o `a_star_maxmin`).
- Activación del registro de estadísticas de planificación.
- Activación de la simulación Monte Carlo.
- Activación de la evaluación cualitativa mediante LLM.

Las definiciones de los experimentos se almacenan automáticamente en:

```text
experiments/definitions/
```

### Ejecutar un experimento de forma interactiva:

```bash
python scripts/run_experiment.py
```

## 📝 Resultados

Los resultados de cada ejecución se almacenan automáticamente en:

```text
experiments/results/
```

Cada archivo de resultados incluye (según configuración):

- Configuración completa del experimento.
- Habilidades iniciales y habilidades objetivo identificadas por el LLM.
- Trayectoria formativa generada.
- Estadísticas del planificador.
- Resultados de la simulación Monte Carlo.
- Evaluación cualitativa realizada por el LLM.
- Tiempo total de ejecución del experimento.

## 📚 Documentación

La descripción detallada del problema, el modelado formal, los algoritmos de planificación implementados, la generación del dataset sintético, la simulación Monte Carlo y la metodología experimental pueden consultarse en el informe incluido en:

```text
docs/
```

## 🤝 Contribución

1. Cree una rama para su funcionalidad:

```bash
git checkout -b feature/nueva-funcionalidad
```

2. Realice commits descriptivos siguiendo convenciones como:

```text
feat: add planner statistics
fix: correct heuristic calculation
docs: update README
```

3. Envíe un Pull Request describiendo claramente los cambios realizados.