# 🎓 Universidad Privada de Tacna
# CURSO: INTELIGENCIA DE NEGOCIOS
## 👨‍🎓 Alumnos
- **Jerson Roni Chambi Cori**
- **Jaime Elias Flores Quispe**
- **Elvis Ronald Leyva Sardon**

# Dashboard de Monitoreo de Repositorios Académicos en GitHub

Sistema para la **evaluación automática y monitoreo** de repositorios académicos de estudiantes de la Facultad de Ingeniería de Sistemas, Universidad Privada de Tacna. Facilita el análisis de métricas de contribución, calidad del código, uso de buenas prácticas y tecnologías empleadas, además de proveer dashboards y reportes para docentes y estudiantes.

---

## Descripción General

Esta herramienta automatiza la revisión de repositorios GitHub usados en cursos académicos, permitiendo:

- **Reducción del tiempo de evaluación docente**.
- **Estandarización de buenas prácticas** en el desarrollo.
- **Reportes analíticos** y métricas objetivas de desempeño.
- **Transparencia y retroalimentación** inmediata para estudiantes.

---

## Objetivos

- **Automatizar** la evaluación de repositorios, reduciendo el tiempo de revisión manual.
- **Estandarizar** criterios de calidad y buenas prácticas en el desarrollo de software.
- **Generar reportes** e identificar tendencias tecnológicas en los proyectos estudiantiles.
- **Mejorar la transparencia** y objetividad en la calificación.

---

## Funcionalidades Principales

- Autenticación con GitHub (OAuth2).
- Extracción y análisis de commits, ramas, issues, pull requests.
- Cálculo automático de métricas de actividad y tecnologías usadas.
- Dashboards interactivos y reportes exportables (PDF/CSV).
- Integración con Power BI.
- Verificación automática de documentación (README.md, informes técnicos).

---

## Requerimientos Funcionales

| ID     | Requerimiento                               | Descripción                                                                 | Prioridad |
|--------|---------------------------------------------|-----------------------------------------------------------------------------|-----------|
| RF-01  | Analizar actividad en repositorios          | Extraer y presentar datos sobre commits, ramas, issues y pull requests.     | Alta      |
| RF-02  | Generar métricas de actividad               | Calcular estadísticas sobre frecuencia de contribución y actividad.         | Alta      |
| RF-03  | Identificar tecnologías utilizadas          | Detectar lenguajes de programación y frameworks en los repositorios.        | Alta      |
| RF-04  | Visualizar reportes interactivos de actividad| Mostrar gráficos y tendencias de desarrollo.                                | Media     |

---

## Diagramas en Mermaid

### Diagrama de Arquitectura

```mermaid
flowchart TD
    github[GitHub]:::github
    actions[GitHub Actions]:::actions
    etl[Script Python ETL]:::etl
    storage[Azure Storage Account]:::storage
    sql[Azure SQL Database]:::sql
    powerbi[Power BI]:::powerbi
    user[Usuario Final]:::user

    github -->|Trigger| actions
    actions -->|Ejecuta script| etl
    etl -->|Escribe CSV/SCRIPT| storage
    etl -->|Carga datos| sql
    storage -->|Importación opcional| sql
    sql -->|Provee datos| powerbi
    powerbi -->|Dashboards,\nReportes| user

    classDef github fill:#f0f8ff,stroke:#000,stroke-width:1px,color:#222;
    classDef actions fill:#ffffe0,stroke:#000,stroke-width:1px,color:#222;
    classDef etl fill:#90ee90,stroke:#000,stroke-width:1px,color:#222;
    classDef storage fill:#87ceeb,stroke:#000,stroke-width:1px,color:#222;
    classDef sql fill:#add8e6,stroke:#000,stroke-width:1px,color:#222;
    classDef powerbi fill:#f5deb3,stroke:#000,stroke-width:1px,color:#222;
    classDef user fill:#ffc0cb,stroke:#000,stroke-width:1px,color:#222;
```

---

### Diagrama de Casos de Uso

```mermaid
flowchart LR
    Scheduler["Scheduler (Crontab)"]
    User["Usuario"]

    subgraph "Sistema ETL / Dashboard Power BI"
      UC1["Actualizar datos periódicamente automáticamente"]
      UC2["Visualizar dashboard en Power BI"]
      UC3["Ejecutar filtros en dashboard"]
    end

    Scheduler --> UC1
    User --> UC2
    User --> UC3
```

---

### Diagrama de Secuencia

```mermaid
%% Diagrama 1: Proceso automático ETL
sequenceDiagram
    participant Scheduler
    participant ETL as "Sistema ETL"
    participant DataSource as "Fuente de datos"
    participant Database as "Base de datos"
    participant Artifacts as "Artefactos de visualización"

    Scheduler->>ETL: Dispara proceso según intervalo
    ETL->>DataSource: Extraer datos
    alt Datos extraídos correctamente
        ETL->>ETL: Transformar y limpiar datos
        ETL->>Database: Cargar datos limpios
        alt Carga correcta
            ETL->>Artifacts: Actualizar artefactos para visualización
        else Error al cargar datos
            ETL-->>Scheduler: Notificar fallo en carga
        end
    else Error en extracción
        ETL-->>Scheduler: Notificar fallo en conexión o script ETL
    end
```

```mermaid
%% Diagrama 2: Visualizar dashboard en Power BI
sequenceDiagram
    participant Usuario
    participant Dashboard as "Dashboard Power BI"
    participant Database as "Base de datos"

    Usuario->>Dashboard: Abre sitio web del dashboard
    Dashboard->>Database: Solicita datos actualizados
    alt Datos disponibles
        Database-->>Dashboard: Envía datos
        Dashboard-->>Usuario: Muestra datos y visualizaciones
    else Problemas de acceso o datos
        Dashboard-->>Usuario: Muestra error o datos desactualizados
    end
    Usuario->>Dashboard: Navega entre vistas y gráficos
```

```mermaid
%% Diagrama 3: Ejecutar filtros en dashboard
sequenceDiagram
    participant Usuario
    participant Dashboard as "Dashboard Power BI"
    participant Database as "Base de datos"

    Usuario->>Dashboard: Selecciona filtros
    Dashboard->>Database: Solicita datos filtrados
    alt Datos filtrados disponibles
        Database-->>Dashboard: Envía datos filtrados
        Dashboard-->>Usuario: Actualiza visualizaciones
    else Filtros sin resultados o error
        Dashboard-->>Usuario: Muestra mensaje de error o sin resultados
    end
```

---

## Reglas de Negocio

- Solo se analizan repositorios públicos de la organizacion con permisos autorizados.
- El usuario puede seleccionar un filtro de año y mes para el análisis.
- Para ser considerado válido, un repositorio debe tener al menos un commit y archivos fuente/documentación.
- Debe existir un archivo `README.md` y al menos un informe técnico (.docx o .md).
- La detección de tecnologías se realiza automáticamente.

---

## Recomendaciones

- Mantener el `README.md` actualizado y con enlaces a los diagramas Mermaid.
- Garantizar la existencia de documentación técnica y archivos requeridos en cada repositorio monitoreado.
- Incentivar el uso de issues y pull requests para mejorar la colaboración y trazabilidad.
- Implementar talleres periódicos sobre buenas prácticas en GitHub para estudiantes y docentes.
- Considerar la integración futura con LMS como Moodle para centralizar la información académica.

---

# ENLACE DE DASHBOARD

https://app.powerbi.com/links/VtN9HA7oPn?ctid=b6b466ee-468d-4011-b9fc-fbdcf82ac90a&pbi_source=linkShare

![image](https://github.com/user-attachments/assets/cabfa55f-012d-4b83-bd14-5ef95a8221b9)


