from github import Github
import pandas as pd
import os
import csv
from datetime import datetime

# -----------------------
# CONFIGURACIÓN
# -----------------------
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
print(f"Token empieza con: {GITHUB_TOKEN[:6] if GITHUB_TOKEN else 'Token vacío!'}")
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')  # <-- Cámbialo por seguridad en producción
ORG_NAME = 'UPT-FAING-EPIS'
OUTPUT_FOLDER = 'github_scraper/data'
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
LIMITE_REPOS = 24  # Limitar a 10 repositorios
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# -----------------------
# INICIO DE SESIÓN
# -----------------------

g = Github(GITHUB_TOKEN)
org = g.get_organization(ORG_NAME)
repos = list(org.get_repos())[:LIMITE_REPOS]  # Solo tomar los primeros 10 repositorios

# -----------------------
# EXTRAER DATOS
# -----------------------

# Listas para almacenar los datos
repos_info = []
commits_info = []
branches_info = []
issues_info = []
pull_requests_info = []

print(f"📊 Analizando {len(repos)} repositorios (de un total disponible)...")

for i, repo in enumerate(repos, 1):
    print(f'[{i}/{len(repos)}] Analizando repositorio: {repo.name}')
    
    # Datos del repositorio
    repo_data = {
        'repo_id': repo.id,
        'nombre': repo.name,
        'nombre_completo': repo.full_name,
        'descripcion': repo.description,
        'rama_principal': repo.default_branch,
        'lenguaje_principal': repo.language,
        'fecha_creacion': repo.created_at,
        'ultima_actualizacion': repo.updated_at,
        'ultimo_push': repo.pushed_at,
        'cantidad_forks': repo.forks_count,
        'cantidad_stars': repo.stargazers_count,
        'cantidad_watchers': repo.watchers_count,
        'cantidad_issues_abiertos': repo.open_issues_count,
    }
    repos_info.append(repo_data)

    # Commits
    try:
        commits = repo.get_commits()
        for commit in commits:
            commit_data = {
                'repo_id': repo.id,
                'commit_sha': commit.sha,
                'author': commit.author.login if commit.author else None,
                'fecha_commit': commit.commit.author.date,
                'mensaje_commit': commit.commit.message
            }
            commits_info.append(commit_data)
    except Exception as e:
        print(f"⚠️ Error extrayendo commits del repo {repo.name}: {e}")

    # Branches
    try:
        branches = repo.get_branches()
        for branch in branches:
            branch_data = {
                'repo_id': repo.id,
                'nombre_rama': branch.name,
                'es_default': branch.name == repo.default_branch
            }
            branches_info.append(branch_data)
    except Exception as e:
        print(f"⚠️ Error extrayendo ramas del repo {repo.name}: {e}")

    # Issues
    try:
        issues = repo.get_issues(state='all')
        for issue in issues:
            # Solo considerar issues que no sean pull requests
            if not issue.pull_request:
                issue_data = {
                    'repo_id': repo.id,
                    'issue_id': issue.id,
                    'titulo_issue': issue.title,
                    'estado_issue': issue.state,
                    'creador': issue.user.login,
                    'fecha_creacion': issue.created_at,
                    'fecha_cierre': issue.closed_at
                }
                issues_info.append(issue_data)
    except Exception as e:
        print(f"⚠️ Error extrayendo issues del repo {repo.name}: {e}")

    # Pull Requests
    try:
        pulls = repo.get_pulls(state='all')
        for pr in pulls:
            pr_data = {
                'repo_id': repo.id,
                'pull_id': pr.id,
                'titulo_pull': pr.title,
                'estado_pull': pr.state,
                'creador': pr.user.login,
                'fecha_creacion': pr.created_at,
                'fecha_cierre': pr.closed_at
            }
            pull_requests_info.append(pr_data)
    except Exception as e:
        print(f"⚠️ Error extrayendo pull requests del repo {repo.name}: {e}")

# -----------------------
# GUARDAR CSV
# -----------------------

# Guardar todos los CSV con el ID del repositorio como clave para unirlos luego
pd.DataFrame(repos_info).to_csv(os.path.join(OUTPUT_FOLDER, 'repositorios.csv'), index=False)
pd.DataFrame(commits_info).to_csv(os.path.join(OUTPUT_FOLDER, 'commits.csv'), index=False)
pd.DataFrame(branches_info).to_csv(os.path.join(OUTPUT_FOLDER, 'ramas.csv'), index=False)
pd.DataFrame(issues_info).to_csv(os.path.join(OUTPUT_FOLDER, 'issues.csv'), index=False)
pd.DataFrame(pull_requests_info).to_csv(os.path.join(OUTPUT_FOLDER, 'pull_requests.csv'), index=False)

print("✅ Extracción completada. Archivos CSV guardados en 'data'.")

# -----------------------
# MÉTRICAS BÁSICAS
# -----------------------

metrics = {
    'total_repositorios': len(repos_info),
    'total_commits': len(commits_info),
    'total_ramas': len(branches_info),
    'total_issues': len(issues_info),
    'total_pull_requests': len(pull_requests_info),
    'promedio_commits_por_repo': len(commits_info) / len(repos_info) if repos_info else 0,
    'promedio_issues_por_repo': len(issues_info) / len(repos_info) if repos_info else 0,
    'promedio_pull_requests_por_repo': len(pull_requests_info) / len(repos_info) if repos_info else 0,
}
pd.DataFrame([metrics]).to_csv(os.path.join(OUTPUT_FOLDER, 'resumen_metricas.csv'), index=False)

print("✅ Métricas básicas generadas y guardadas.")

# -----------------------
# CONVERSIÓN A SQL
# -----------------------

print("🔄 Iniciando conversión a SQL...")

# Función para formatear fechas para SQL Server
def formatear_fecha(fecha):
    if not fecha or str(fecha).strip() == '':
        return 'NULL'
    try:
        if isinstance(fecha, str):
            fecha_sin_zona = fecha.split('+')[0].strip()
            fecha_obj = datetime.strptime(fecha_sin_zona, '%Y-%m-%d %H:%M:%S')
        else:
            fecha_obj = fecha
        return f"'{fecha_obj.strftime('%Y-%m-%d %H:%M:%S')}'"
    except Exception:
        return 'NULL'

# Archivo SQL unificado
output_sql_file = os.path.join(OUTPUT_FOLDER, 'github_data_insert.sql')

with open(output_sql_file, 'w', encoding='utf-8') as sqlfile:
    # Escribir encabezado
    sqlfile.write("-- Script SQL generado automáticamente para insertar datos de GitHub\n")
    sqlfile.write("-- Fecha de generación: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n\n")
    
    # CREAR TABLAS SI NO EXISTEN
    sqlfile.write("-- ==========================================\n")
    sqlfile.write("-- CREACIÓN DE TABLAS\n")
    sqlfile.write("-- ==========================================\n\n")
    
    sqlfile.write("""-- Crear tabla Repositorios si no existe
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Repositorios')
BEGIN
    CREATE TABLE Repositorios (
        repo_id VARCHAR(250) PRIMARY KEY,  -- SIN IDENTITY
        nombre NVARCHAR(255),
        nombre_completo NVARCHAR(500),
        descripcion NVARCHAR(MAX),
        rama_principal NVARCHAR(100),
        lenguaje_principal NVARCHAR(100),
        fecha_creacion DATETIME,
        ultima_actualizacion DATETIME,
        ultimo_push DATETIME,
        cantidad_forks INT,
        cantidad_stars INT,
        cantidad_watchers INT,
        cantidad_issues_abiertos INT
    );
END

-- Crear tabla Commits si no existe
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Commits')
BEGIN
    CREATE TABLE Commits (
        id INT IDENTITY(1,1) PRIMARY KEY,
        repo_id VARCHAR(250) FOREIGN KEY REFERENCES Repositorios(repo_id),
        sha NVARCHAR(100),
        autor NVARCHAR(255),
        fecha DATETIME,
        mensaje NVARCHAR(MAX)
    );
END

-- Crear tabla Ramas si no existe
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Ramas')
BEGIN
    CREATE TABLE Ramas (
        id INT IDENTITY(1,1) PRIMARY KEY,
        repo_id VARCHAR(250) FOREIGN KEY REFERENCES Repositorios(repo_id),
        nombre NVARCHAR(255),
        es_default VARCHAR(50)
    );
END

-- Crear tabla Issues si no existe
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Issues')
BEGIN
    CREATE TABLE Issues (
        id INT IDENTITY(1,1) PRIMARY KEY,
        repo_id VARCHAR(250) FOREIGN KEY REFERENCES Repositorios(repo_id),
        numero VARCHAR(250),
        titulo NVARCHAR(MAX),
        estado NVARCHAR(50),
        autor NVARCHAR(255),
        creado_en DATETIME,
        cerrado_en DATETIME
    );
END

-- Crear tabla PullRequests si no existe
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'PullRequests')
BEGIN
    CREATE TABLE PullRequests (
        id INT IDENTITY(1,1) PRIMARY KEY,
        repo_id VARCHAR(250) FOREIGN KEY REFERENCES Repositorios(repo_id),
        numero VARCHAR(250),
        titulo NVARCHAR(MAX),
        estado NVARCHAR(50),
        autor NVARCHAR(255),
        creado_en DATETIME,
        cerrado_en DATETIME
    );
END

-- Crear tabla ResumenMetricas si no existe
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'ResumenMetricas')
BEGIN
    CREATE TABLE ResumenMetricas (
        total_repositorios INT,
        total_commits INT,
        promedio_commits_por_repo DECIMAL(10,2)
    );
END

""")
    
    # 1. REPOSITORIOS
    sqlfile.write("\n-- ==========================================\n")
    sqlfile.write("-- INSERCIÓN DE REPOSITORIOS\n")
    sqlfile.write("-- ==========================================\n\n")
    
    repos_csv_file = os.path.join(OUTPUT_FOLDER, 'repositorios.csv')
    valid_repo_ids = set()
    
    with open(repos_csv_file, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            repo_id = row['repo_id'].strip()
            valid_repo_ids.add(repo_id)
            
            nombre = row['nombre'].replace("'", "''")
            nombre_completo = row['nombre_completo'].replace("'", "''")
            descripcion = row['descripcion'].replace("'", "''") if row['descripcion'] else ''
            rama_principal = row['rama_principal'].replace("'", "''") if row['rama_principal'] else ''
            lenguaje = row['lenguaje_principal'].replace("'", "''") if row['lenguaje_principal'] else ''

            fecha_creacion = formatear_fecha(row['fecha_creacion'])
            ultima_actualizacion = formatear_fecha(row['ultima_actualizacion'])
            ultimo_push = formatear_fecha(row['ultimo_push'])

            forks = row['cantidad_forks'].strip() or '0'
            stars = row['cantidad_stars'].strip() or '0'
            watchers = row['cantidad_watchers'].strip() or '0'
            issues_abiertos = row['cantidad_issues_abiertos'].strip() or '0'

            sql = (
                f"IF NOT EXISTS (SELECT 1 FROM Repositorios WHERE repo_id = '{repo_id}')\n"
                f"    INSERT INTO Repositorios (repo_id, nombre, nombre_completo, descripcion, rama_principal, lenguaje_principal, "
                f"fecha_creacion, ultima_actualizacion, ultimo_push, cantidad_forks, cantidad_stars, cantidad_watchers, cantidad_issues_abiertos) "
                f"VALUES ('{repo_id}', '{nombre}', '{nombre_completo}', '{descripcion}', '{rama_principal}', '{lenguaje}', "
                f"{fecha_creacion}, {ultima_actualizacion}, {ultimo_push}, {forks}, {stars}, {watchers}, {issues_abiertos});\n\n"
            )
            sqlfile.write(sql)

    # 2. COMMITS
    sqlfile.write("\n-- ==========================================\n")
    sqlfile.write("-- INSERCIÓN DE COMMITS\n")
    sqlfile.write("-- ==========================================\n\n")
    
    commits_csv_file = os.path.join(OUTPUT_FOLDER, 'commits.csv')
    with open(commits_csv_file, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            repo_id = row['repo_id'].strip()
            if repo_id not in valid_repo_ids:
                continue

            sha = row['commit_sha'].replace("'", "''")
            autor = row['author'].replace("'", "''") if row['author'] else ''
            mensaje = row['mensaje_commit'].replace("'", "''")

            fecha_commit = formatear_fecha(row['fecha_commit'])

            sql = (
                f"IF NOT EXISTS (SELECT 1 FROM Commits WHERE sha = '{sha}')\n"
                f"    INSERT INTO Commits (repo_id, sha, autor, fecha, mensaje) VALUES ('{repo_id}', '{sha}', '{autor}', {fecha_commit}, '{mensaje}');\n\n"
            )
            sqlfile.write(sql)

    # 3. RAMAS
    sqlfile.write("\n-- ==========================================\n")
    sqlfile.write("-- INSERCIÓN DE RAMAS\n")
    sqlfile.write("-- ==========================================\n\n")
    
    ramas_csv_file = os.path.join(OUTPUT_FOLDER, 'ramas.csv')
    with open(ramas_csv_file, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            repo_id = row['repo_id'].strip()
            if repo_id not in valid_repo_ids:
                continue

            nombre_rama = row['nombre_rama'].replace("'", "''")
            es_default = str(row['es_default']).strip()

            sql = (
                f"IF NOT EXISTS (SELECT 1 FROM Ramas WHERE repo_id = '{repo_id}' AND nombre = '{nombre_rama}')\n"
                f"    INSERT INTO Ramas (repo_id, nombre, es_default) "
                f"VALUES ('{repo_id}', '{nombre_rama}', '{es_default}');\n\n"
            )
            sqlfile.write(sql)

    # 4. ISSUES
    sqlfile.write("\n-- ==========================================\n")
    sqlfile.write("-- INSERCIÓN DE ISSUES\n")
    sqlfile.write("-- ==========================================\n\n")
    
    issues_csv_file = os.path.join(OUTPUT_FOLDER, 'issues.csv')
    with open(issues_csv_file, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            repo_id = row['repo_id'].strip()
            if repo_id not in valid_repo_ids:
                continue

            issue_id = row['issue_id']
            titulo = row['titulo_issue'].replace("'", "''")
            estado = row['estado_issue'].replace("'", "''")
            creador = row['creador'].replace("'", "''")

            fecha_creacion = formatear_fecha(row['fecha_creacion'])
            fecha_cierre = formatear_fecha(row['fecha_cierre'])

            sql = (
                f"IF NOT EXISTS (SELECT 1 FROM Issues WHERE repo_id = '{repo_id}' AND numero = '{issue_id}')\n"
                f"    INSERT INTO Issues (repo_id, numero, titulo, estado, autor, creado_en, cerrado_en) "
                f"VALUES ('{repo_id}', '{issue_id}', '{titulo}', '{estado}', '{creador}', {fecha_creacion}, {fecha_cierre});\n\n"
            )
            sqlfile.write(sql)

    # 5. PULL REQUESTS
    sqlfile.write("\n-- ==========================================\n")
    sqlfile.write("-- INSERCIÓN DE PULL REQUESTS\n")
    sqlfile.write("-- ==========================================\n\n")
    
    pulls_csv_file = os.path.join(OUTPUT_FOLDER, 'pull_requests.csv')
    with open(pulls_csv_file, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            repo_id = row['repo_id'].strip()
            if repo_id not in valid_repo_ids:
                continue

            pull_id = row['pull_id'].strip()
            titulo = row['titulo_pull'].replace("'", "''")
            estado = row['estado_pull'].replace("'", "''")
            creador = row['creador'].replace("'", "''")

            fecha_creacion = formatear_fecha(row['fecha_creacion'])
            fecha_cierre = formatear_fecha(row['fecha_cierre'])

            sql = (
                f"IF NOT EXISTS (SELECT 1 FROM PullRequests WHERE repo_id = '{repo_id}' AND numero = '{pull_id}')\n"
                f"    INSERT INTO PullRequests (repo_id, numero, titulo, estado, autor, creado_en, cerrado_en) "
                f"VALUES ('{repo_id}', '{pull_id}', '{titulo}', '{estado}', '{creador}', {fecha_creacion}, {fecha_cierre});\n\n"
            )
            sqlfile.write(sql)

print(f"🎉 Script SQL unificado generado: {output_sql_file}")
print("✅ Proceso completado exitosamente.")