# Traducción en vivo — Inglés → Español (app de escritorio)

Aplicación de escritorio en Python que escucha el micrófono, transcribe lo
que se dice en inglés, lo traduce al español y lo muestra en pantalla
(con opción de leerlo en voz alta). Pensada para proyectar la traducción
durante una charla o conferencia.

## 1. Instalar Python

Necesitás Python 3.9 o superior. Verificá con:

```
python3 --version
```

Si no lo tenés, descargalo de https://www.python.org/downloads/

## 2. Instalar dependencias del sistema (antes que las de Python)

`PyAudio` necesita una librería del sistema llamada `portaudio`.

**Windows:** no necesita nada extra normalmente; si falla la instalación de
PyAudio, instalá el paquete precompilado con:
```
pip install pipwin
pipwin install pyaudio
```

**macOS:**
```
brew install portaudio
```

**Linux (Ubuntu/Debian):**
```
sudo apt-get install portaudio19-dev python3-pyaudio
```

## 3. Instalar las dependencias de Python

Dentro de la carpeta del proyecto:

```
python3 -m venv venv
source venv/bin/activate        # en Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 4. Ejecutar la aplicación

```
python3 main.py
```

Se abre una ventana con:
- Botón **Iniciar traducción** / **Detener traducción**.
- Panel superior: lo que se transcribió en inglés.
- Panel inferior (letra grande, ideal para proyectar): la traducción al español.
- Casillero **Leer traducción en voz alta**: si lo activás, la app lee el
  español con una voz del sistema.
- Selector de **Voz**, botones **A− / A+** para el tamaño de letra.
- **Guardar transcripción**: exporta un .txt con todo lo dicho y traducido.

## Cómo funciona por dentro

- **Reconocimiento de voz:** usa el reconocedor gratuito de Google a través
  de la librería `SpeechRecognition` (necesita internet).
- **Traducción:** usa `deep-translator` (Google Translate) para pasar cada
  frase de inglés a español.
- **Voz en español:** usa `pyttsx3`, que habla con las voces ya instaladas
  en tu sistema operativo (no necesita internet, pero la calidad de la voz
  depende de las voces en español que tengas instaladas en Windows/macOS/Linux).

## Limitaciones a tener en cuenta

- Necesita internet estable (el reconocimiento y la traducción son servicios
  en la nube gratuitos, con límites de uso razonables).
- La latencia es de 1 a 3 segundos por frase — es una traducción "casi
  simultánea", no instantánea como un intérprete humano.
- La calidad de transcripción baja si hay mucho ruido de fondo o varias
  personas hablando a la vez; funciona mejor con un micrófono cerca del
  orador.
- Para eventos grandes o profesionales, esto es un buen apoyo o prototipo,
  pero no reemplaza interpretación simultánea profesional (equipos de
  cabina, FM/infrarrojo, o plataformas como Interprefy/KUDO).

## Generar el .exe automáticamente con GitHub Actions (sin usar Windows vos)

Esta carpeta ya incluye `.github/workflows/build.yml`, que hace que
**GitHub compile el .exe por vos**, en una PC Windows virtual en la nube,
cada vez que subís el código. Solo necesitás una cuenta de GitHub
(gratis).

### Paso 1 — Crear el repositorio

1. Entrá a https://github.com y creá una cuenta si no tenés.
2. Arriba a la derecha, botón **"+"** → **"New repository"**.
3. Ponele un nombre, por ejemplo `traductor-en-vivo`. Puede ser privado o
   público (privado también funciona con Actions). Creá el repositorio.

### Paso 2 — Subir esta carpeta

La forma más simple, sin usar la terminal:

1. En la página del repositorio recién creado, hacé clic en
   **"uploading an existing file"** (o "Add file" → "Upload files").
2. Arrastrá **todo el contenido** de esta carpeta (incluida la subcarpeta
   `.github`, que puede no verse en el explorador de Windows si tenés
   ocultos los archivos que empiezan con punto — activá "mostrar archivos
   ocultos" para verla).
3. Hacé clic en **"Commit changes"**.

(Si preferís usar git por línea de comandos: `git init`, `git add .`,
`git commit -m "primera version"`, `git remote add origin <URL-de-tu-repo>`,
`git push -u origin main`.)

### Paso 3 — Ver cómo compila y descargar el resultado

1. En el repositorio, andá a la pestaña **"Actions"**.
2. Vas a ver un workflow corriendo ("Compilar Traductor en Vivo (Windows)").
   Tarda 2-4 minutos.
3. Cuando termine (tilde verde), entrá a esa ejecución y bajá hasta
   **"Artifacts"**. Ahí vas a encontrar dos archivos para descargar:
   - **`TraductorEnVivo-exe`** → el ejecutable suelto.
   - **`TraductorEnVivo-Setup`** → el instalador con ícono y desinstalador
     (recomendado para repartir en varias PCs).

Cada descarga es un .zip que contiene el archivo real adentro.

### Paso 4 — (Opcional) Un link de descarga fijo con "Releases"

Los Artifacts de Actions requieren estar logueado en GitHub y expiran
después de un tiempo. Si querés un **link permanente** para mandar a otras
personas sin que necesiten cuenta de GitHub (repo público):

1. En el repositorio, andá a **"Releases"** → **"Create a new release"**.
2. En "Tag", escribí algo como `v1.0` y publicá el release.
3. Eso dispara de nuevo el workflow, que esta vez además **adjunta los dos
   archivos directamente en la página del Release**, con un link estable
   que cualquiera puede abrir y descargar.

### Cómo instalarlo en cada computadora

Copiá `TraductorEnVivo-Setup.exe` (por red, pendrive, o el link del
Release) a cada PC y ejecutalo. Instala la app con ícono en el escritorio
y menú inicio, sin necesitar Python instalado en esas máquinas.

### Alternativa: compilarlo vos mismo en una PC Windows

Si en algún momento preferís no depender de GitHub, `build_exe.bat` e
`installer.iss` siguen funcionando de forma local en cualquier PC Windows
con Python — son los mismos pasos que ejecuta el workflow, pero a mano.

### Nota sobre Windows SmartScreen / antivirus

Como el .exe no tiene firma digital de un desarrollador reconocido, es
probable que la primera vez que se ejecute en cada PC, Windows muestre un
aviso ("Windows protegió su PC"). Se resuelve haciendo clic en **"Más
información" → "Ejecutar de todas formas"**. Esto es normal para software
sin firmar y no significa que esté dañado; si necesitás evitar ese aviso
en muchas PCs de una empresa, la opción es comprar un certificado de firma
de código (tiene costo) o distribuirlo a través de una política interna
que lo autorice.
