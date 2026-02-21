import streamlit as st
import random
import time
from streamlit_autorefresh import st_autorefresh  # pip install streamlit-autorefresh

st.set_page_config(
    page_title="Tablas",
    page_icon="🧠",
    menu_items={
        'About': None,          # Elimina la opción "About" del menú (opcional)
        'Report a Bug': None,   # Elimina "Report a Bug" (opcional)
        'Get help': None        # Elimina "Get help" (opcional)
    }
)

# ---------------- ESTADOS ----------------
if "pantalla" not in st.session_state:
    st.session_state.pantalla = "inicio"

if "tabla" not in st.session_state:
    st.session_state.tabla = 1

if "limite" not in st.session_state:
    st.session_state.limite = 10

if "pendientes" not in st.session_state:
    st.session_state.pendientes = []          # números que aún no se han acertado

if "pregunta" not in st.session_state:
    st.session_state.pregunta = None

if "respuesta_correcta" not in st.session_state:
    st.session_state.respuesta_correcta = None

if "inicio_tiempo" not in st.session_state:
    st.session_state.inicio_tiempo = None

if "correctas" not in st.session_state:
    st.session_state.correctas = 0

if "incorrectas" not in st.session_state:
    st.session_state.incorrectas = 0

if "intentos" not in st.session_state:
    st.session_state.intentos = 0


# ---------------- FUNCIÓN NUEVA PREGUNTA ----------------
def nueva_pregunta():
    # Si ya no quedan números por acertar, ir a pantalla final
    if not st.session_state.pendientes:
        st.session_state.pantalla = "fin"
        return

    numero = random.choice(st.session_state.pendientes)
    st.session_state.pregunta = f"{st.session_state.tabla} x {numero}"
    st.session_state.respuesta_correcta = st.session_state.tabla * numero
    st.session_state.inicio_tiempo = time.time()


# =====================================================
# =================== PANTALLA INICIO =================
# =====================================================
if st.session_state.pantalla == "inicio":

    st.title("🧠 Practicador de Tablas")

    tabla = st.selectbox("¿Qué tabla quieres practicar?", range(1, 21))
    limite = st.number_input(
        "¿Hasta qué número?",
        min_value=1,
        max_value=100,
        value=10
    )

    nivel = st.selectbox("Nivel", ["Fácil", "Medio (10s)", "Difícil (5s)"])

    if st.button("🚀 Comenzar"):
        st.session_state.tabla = tabla
        st.session_state.limite = limite
        st.session_state.nivel = nivel
        st.session_state.correctas = 0
        st.session_state.incorrectas = 0
        st.session_state.intentos = 0
        st.session_state.pendientes = list(range(1, limite + 1))  # todos pendientes
        st.session_state.pantalla = "conteo"
        st.rerun()


# =====================================================
# =================== CONTEO 3 2 1 ====================
# =====================================================
elif st.session_state.pantalla == "conteo":

    st.title("Prepárate...")
    espacio = st.empty()

    for i in range(3, 0, -1):
        espacio.markdown(f"# {i}")
        time.sleep(1)

    st.session_state.pantalla = "juego"
    nueva_pregunta()
    st.rerun()


# =====================================================
# =================== PANTALLA JUEGO ==================
# =====================================================
elif st.session_state.pantalla == "juego":

    # -------- TEMPORIZADOR EN TIEMPO REAL (autorefresh) --------
    if "Fácil" not in st.session_state.nivel:
        st_autorefresh(interval=1000, key="timer_refresh")

    st.title("🔥 ¡Responde!")

    if st.button("⬅ Volver al inicio"):
        st.session_state.pantalla = "inicio"
        st.rerun()

    st.subheader(f"📌 {st.session_state.pregunta}")

    # Determinar tiempo
    if "Fácil" in st.session_state.nivel:
        tiempo_limite = None
    elif "10" in st.session_state.nivel:
        tiempo_limite = 10
    else:
        tiempo_limite = 5

    # -------- CONTROL DE TIEMPO --------
    if tiempo_limite is not None:
        tiempo_pasado = time.time() - st.session_state.inicio_tiempo
        tiempo_restante = tiempo_limite - tiempo_pasado

        if tiempo_restante <= 0:
            st.session_state.intentos += 1
            st.session_state.incorrectas += 1
            st.toast(f"⏰ ¡Tiempo agotado! La respuesta era {st.session_state.respuesta_correcta}", icon="⌛")
            nueva_pregunta()
            # No necesitamos rerun porque el autorefresh lo hará
        else:
            porcentaje = max(0, tiempo_restante / tiempo_limite)
            st.progress(porcentaje)
            st.write(f"⏳ {int(tiempo_restante)} segundos")

    # -------- FORMULARIO --------
    with st.form("form_respuesta", clear_on_submit=True):
        respuesta = st.text_input("Tu respuesta:")
        enviar = st.form_submit_button("Responder")

    if enviar:
        if respuesta.isdigit():
            st.session_state.intentos += 1
            resp_num = int(respuesta)

            if resp_num == st.session_state.respuesta_correcta:
                # Correcto
                st.session_state.correctas += 1
                num_pregunta = int(st.session_state.pregunta.split(" x ")[1])
                if num_pregunta in st.session_state.pendientes:
                    st.session_state.pendientes.remove(num_pregunta)

                if "Fácil" in st.session_state.nivel:
                    # Mostrar overlay de felicitación
                    st.markdown(
                        """
                        <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0, 255, 0, 0.08); z-index: 9999; display: flex; flex-direction: column; justify-content: center; align-items: center;">
                            <h1 style="font-size: 100px; margin: 0;">🎉</h1>
                            <h2 style="color: green; margin: 0;">¡Correcto!</h2>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    time.sleep(1)
                    nueva_pregunta()
                    st.rerun()
                else:
                    st.toast("✅ ¡Correcto!", icon="🎉")
                    nueva_pregunta()
            else:
                # Incorrecto
                st.session_state.incorrectas += 1

                if "Fácil" in st.session_state.nivel:
                    # Mostrar overlay de error con la respuesta correcta
                    st.markdown(
                        f"""
                        <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(255, 0, 0, 0.08); z-index: 9999; display: flex; flex-direction: column; justify-content: center; align-items: center;">
                            <h1 style="font-size: 100px; margin: 0;">❌</h1>
                            <h2 style="color: white; margin: 0;">Incorrecto. La respuesta era {st.session_state.respuesta_correcta}</h2>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    time.sleep(1)
                    nueva_pregunta()
                    st.rerun()
                else:
                    st.toast(f"❌ Incorrecto. La respuesta era {st.session_state.respuesta_correcta}", icon="😓")
                    nueva_pregunta()
        else:
            st.warning("Escribe un número válido.")

    # -------- ESTADÍSTICAS --------
    st.divider()
    col1, col2, col3 = st.columns(3)
    col1.metric("Intentos", st.session_state.intentos)
    col2.metric("Correctas", st.session_state.correctas)
    col3.metric("Incorrectas", st.session_state.incorrectas)

    if st.session_state.intentos > 0:
        precision = st.session_state.correctas / st.session_state.intentos * 100
        st.progress(precision / 100)
        st.write(f"🎯 Precisión: {precision:.1f}%")


# =====================================================
# =================== PANTALLA FINAL ==================
# =====================================================
elif st.session_state.pantalla == "fin":
    st.balloons()
    st.title("🎉 ¡Felicidades! 🎉")
    st.write("Has respondido correctamente todas las preguntas de esta tabla.")
    st.write(f"**Totales:** {st.session_state.intentos} intentos, "
             f"{st.session_state.correctas} correctas, "
             f"{st.session_state.incorrectas} incorrectas.")
    if st.button("Volver a empezar"):
        st.session_state.pantalla = "inicio"
        st.rerun()