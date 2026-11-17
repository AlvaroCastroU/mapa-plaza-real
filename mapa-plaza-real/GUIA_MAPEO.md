# Guía de mapeo: ¿Qué tan fácil es caminar por Plaza Real?

> Guía para cualquier persona, aunque nunca haya usado OSMTracker ni GitHub.
> Tiempo para prepararse: unos 15 minutos (solo la primera vez). Tiempo de mapeo: lo que usted quiera.

---

## 1. ¿Qué es este mapa y para qué sirve?

Es un **mapa en internet, hecho entre varias personas**, que muestra qué tan fácil, cómodo y seguro es moverse a pie por **Plaza Real (Alajuela)**. Esto incluye a personas en silla de ruedas, con coche de bebé, con bastón o adultas mayores.

En el mapa se marcan cosas como:

- **Rampas, escaleras y obstáculos** que facilitan o impiden el paso.
- **El estado de las aceras** (buenas o dañadas).
- **Bancas, basureros, bebederos, luz, sombra y árboles.**
- **Cómo se siente la gente** en cada lugar: segura, insegura, a gusto, con mucho ruido, con poca luz…

Cada persona que camina con su celular y la app **OSMTracker** agrega información. Unos minutos después, el mapa se actualiza solo y cualquiera puede verlo.

**¿Para qué?** Para saber qué rutas sirven a todas las personas, qué hay que arreglar y tener datos concretos para pedir mejoras a la administración del lugar o a la municipalidad.

🔗 **Ver el mapa:** `https://USUARIO.github.io/mapa-plaza-real/`

---

## 2. Lo que necesita

- Un celular **Android** con GPS.
- La app **OSMTracker for Android** (gratis). Búsquela así en Google Play o en F-Droid.
- Una **cuenta de GitHub** (gratis, en https://github.com). Solo se usa para enviar sus recorridos al mapa.
- Que el grupo le haya agregado como **colaborador(a)** del repositorio del mapa (pídalo con su nombre de usuario de GitHub).

---

## 3. Instalar los botones del mapa en OSMTracker

OSMTracker muestra una pantalla de botones. Nosotros hicimos un juego de botones especial para este mapa: la **disposición «accesibilidad plaza real»**.

1. Abra OSMTracker y toque el menú **⋮** (arriba a la derecha) → **Configuración**.
2. Baje hasta **Interfaz de usuario** → **Disposición de los botones**.
3. Toque el menú **⋮** → **Disposiciones para descargar**.
4. Toque **⋮** → **Configuración del Repositorio GitHub**, marque **Personalizado** y escriba:
   - Nombre de usuario GitHub: `AlvaroCastroU`
   - Nombre del Repositorio: `osmtracker-android-layouts`
   - Nombre de la rama: `master`

   Debe aparecer el mensaje **«Repositorio de GitHub válido»**. Guarde.
5. En la lista, toque **accesibilidad plaza real** → **Descargar**.
6. Vuelva a **Disposición de los botones** y **marque «accesibilidad plaza real»**.

📷 *[Captura 1: pantalla de configuración del repositorio]*
📷 *[Captura 2: lista de disposiciones con «accesibilidad plaza real»]*

---

## 4. Cómo mapear en el lugar

### 4.1 Empezar un recorrido

1. Vaya a Plaza Real y abra OSMTracker.
2. Toque **+ (Nueva traza)**. Espere a que los botones se activen: eso significa que ya hay señal GPS (al aire libre tarda menos de un minuto).
3. Camine con normalidad. **La app va dibujando su recorrido sola.**

### 4.2 Qué botón usar

Toque un botón **cuando esté parado justo encima o al lado** de lo que quiere marcar.

**Pantalla principal**

| Botón | Úselo cuando… |
|---|---|
| **Rampa** | Hay una rampa para silla de ruedas o coche de bebé. |
| **Escaleras** | Hay gradas o escaleras (son una barrera para sillas de ruedas). |
| **Obstáculo** | Algo bloquea el paso: poste, carro mal parqueado, macetas, materiales, hueco… |
| **Acera buena** | **A partir de aquí** la acera está en buen estado. |
| **Acera dañada** | **A partir de aquí** la acera está rota, desnivelada o resbalosa. |
| **Baño accesible** | Hay un baño para personas con discapacidad. |
| **Parqueo discapacidad** | Hay un espacio de parqueo para personas con discapacidad. |
| **Mobiliario ➜** | Abre otra página con bancas, basureros, etc. |
| **Percepción ➜** | Abre otra página para decir cómo se siente en ese lugar. |

> 💡 **Truco de las aceras:** al empezar a caminar toque **Acera buena** o **Acera dañada** según cómo esté. Cada vez que la acera cambie, toque el otro botón. Así el mapa pinta su recorrido en **verde** (buena) o **rojo** (dañada).

**Página «Mobiliario»:** Banca · Basurero · Bebedero · Iluminación · Sombra · Árbol.

**Página «Percepción»:** Me siento seguro · Me siento inseguro · Lugar agradable · Ruido excesivo · Poca luz · Zona descuidada.

Para regresar a la pantalla principal use el botón **Atrás** del celular.

### 4.3 Fotos, audios y notas

Arriba de cada página hay tres botones:

- 🎤 **Audio:** grabe un comentario corto (por ejemplo: «esta rampa está muy empinada»).
- 📷 **Foto:** tome una foto de lo que marcó.
- 📝 **Nota:** escriba un texto corto.

> 💡 **Tome la foto, audio o nota justo después de tocar el botón** (en menos de un minuto y medio). Así el mapa los pone **dentro del mismo punto** y al tocarlo se ven juntos.

### 4.4 Terminar

Cuando termine, toque el menú **⋮** → **Detener y guardar**.

📷 *[Captura 3: pantalla de botones durante el mapeo]*

---

## 5. Enviar el recorrido al mapa (subir a GitHub)

**Solo la primera vez: crear su «token» (una contraseña especial para la app)**

1. Entre a https://github.com/settings/tokens desde el navegador (con su cuenta iniciada).
2. Elija **Tokens (classic)** → **Generate new token (classic)**.
3. Póngale un nombre (por ejemplo «OSMTracker»), elija la fecha de vencimiento y marque la casilla **repo**.
4. Toque **Generate token** y **copie** el código (empieza con `ghp_` y tiene 40 caracteres).

   ⚠️ Debe ser un token **classic**: los otros tipos son más largos y la app los rechaza.

**Cada vez que quiera subir un recorrido**

1. En la lista de trazas de OSMTracker, **mantenga presionado** el recorrido.
2. Toque **Subir a GitHub**.
3. La primera vez la app pedirá **Configure**: escriba su usuario de GitHub, pegue el token y guarde.
4. En **Seleccione el repositorio** elija `mapa-plaza-real`.
5. En **Mensaje del commit** escriba algo corto, por ejemplo: «Recorrido entrada principal – María».
6. Toque **Commit**. ¡Listo! La app envía un archivo `.zip` con su recorrido, fotos y audios.

📷 *[Captura 4: menú al mantener presionada la traza]*
📷 *[Captura 5: pantalla «Subir a GitHub» con el repositorio y el mensaje]*

---

## 6. Ver el mapa

Abra 🔗 `https://USUARIO.github.io/mapa-plaza-real/` en cualquier celular o computadora.

Unos **2 a 5 minutos** después de subir un recorrido, el mapa se actualiza solo. Si no ve los cambios, recargue la página.

Lo que puede hacer en el mapa:

| Elemento | Qué muestra |
|---|---|
| **Puntos de colores** | Cada botón que alguien tocó. Toque un punto para ver **foto, audio, nota**, fecha y quién lo aportó. |
| **Círculos con número** | Varios puntos juntos (agrupados). Toque el círculo para acercarse. |
| **Mapa de calor** | Las zonas con **más reportes** se ven rojas; las de pocos, azules. |
| **Líneas verdes / rojas / grises** | Los recorridos: verde = acera buena, rojo = acera dañada, gris = sin clasificar. |
| **«¿De cuándo son los datos?»** | Mueva la barra para **ocultar los recorridos viejos**. «Último día / semana / mes» filtra rápido. **«Mostrar todas»** vuelve a mostrar todo. |
| **«¿Qué mostrar?»** | Marque o desmarque tipos de puntos (por ejemplo, ver solo obstáculos). |
| **Botón de capas (arriba a la derecha)** | Cambiar entre mapa y foto satelital. |

📷 *[Captura 6: el mapa con puntos, recorridos y una foto abierta]*

---

## 7. Recomendaciones

- Mapee de **día y de noche**: la sensación de seguridad y la iluminación cambian mucho.
- No se ponga en riesgo para tomar una foto ni fotografíe de cerca la cara de otras personas.
- Si se equivoca de botón, no pasa nada: tóquelo de nuevo en el lugar correcto y agregue una 📝 nota explicando.
