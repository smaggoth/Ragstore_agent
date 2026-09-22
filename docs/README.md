# Proyecto RAG con Agentes Orquestados

## Descripción General

Este proyecto implementa un sistema de recuperación aumentada por generación (RAG) combinado con un agente orquestado, capaz de responder preguntas consultando tanto una base de conocimiento local (documentos Markdown) como la web en tiempo real. El sistema se expone como una API REST, accesible de forma remota desde cualquier dispositivo.

## Objetivo

El propósito de este proyecto es construir, de principio a fin, un sistema de GenAI aplicado que combine búsqueda semántica, orquestación de agentes, y consumo de LLMs, replicando el tipo de arquitectura usada en sistemas de producción reales.

## Arquitectura

El sistema se compone de las siguientes piezas:

- **Almacén vectorial (Qdrant)**: base de datos vectorial que soporta búsqueda híbrida, combinando similitud semántica (embeddings) con búsqueda por palabras clave.
- **Generación de embeddings (Gemini)**: los documentos y las consultas del usuario se convierten en vectores densos usando el modelo de embeddings de Google Gemini.
- **Agente orquestador (LangGraph)**: decide, para cada consulta del usuario, si la respuesta debe buscarse en la base de conocimiento local o en la web.
- **Búsqueda web (Tavily)**: herramienta de búsqueda en tiempo real, integrada como parte de las herramientas disponibles para el agente.
- **Modelo de lenguaje (Gemini)**: genera la respuesta final en lenguaje natural, a partir del contexto recuperado.
- **API (FastAPI)**: expone todo el sistema como un servicio REST, con endpoints para consultar, administrar documentos, y revisar el historial de conversaciones.

## Fases de Construcción

### Fase 1: Ingesta y Almacenamiento

En esta fase se implementa la lectura de documentos Markdown, su división en fragmentos (chunking), la generación de embeddings para cada fragmento usando la API de Gemini, y su almacenamiento en Qdrant.

### Fase 2: Búsqueda Híbrida

Se implementa la lógica de recuperación: dado un query del usuario, se genera su embedding, se realiza una búsqueda combinada de similitud vectorial y coincidencia de palabras clave, y se regresan los fragmentos más relevantes.

### Fase 3: Agente con LangGraph

Se construye un agente capaz de decidir entre dos rutas posibles: consultar la base de conocimiento local, o realizar una búsqueda web mediante Tavily. El agente utiliza Gemini como modelo de razonamiento para generar la respuesta final.

### Fase 4: Envoltura en API

Se exponen los componentes anteriores mediante FastAPI, integrando validación de datos con Pydantic y pruebas automatizadas con pytest.

### Fase 5: Acceso Remoto

Se configura el sistema para ser accesible desde otros dispositivos en la misma red local, o de forma remota mediante un túnel temporal, permitiendo su uso sin depender de estar frente a la máquina donde corre el servidor.

## Requisitos Previos

- Python 3.13 o superior, gestionado con `uv`.
- Docker, para levantar la instancia local de Qdrant.
- Una clave de API de Google Gemini.
- Una clave de API de Tavily.

## Instalación

1. Clonar el repositorio del proyecto.
2. Instalar las dependencias con `uv sync`.
3. Levantar Qdrant mediante Docker, exponiendo los puertos 6333 y 6334.
4. Configurar las variables de entorno necesarias para las claves de API.
5. Ejecutar el servidor de desarrollo con `uv run uvicorn main:app --reload`.

## Estado Actual

El proyecto se encuentra en su fase inicial de desarrollo, correspondiente a la ingesta y almacenamiento de documentos en el almacén vectorial.
