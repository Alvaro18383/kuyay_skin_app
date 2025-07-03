import streamlit as st
from PIL import Image
import numpy as np
from utils_nocv2 import analizar_piel, es_rostro_valido
from datetime import datetime
import random
from utils_db_mysql import crear_db, guardar_diagnostico, guardar_cuestionario, cargar_diagnostico, cargar_cuestionario
from utils_db_mysql import registrar_usuario
import pandas as pd
from utils_db_mysql import registrar_usuario, verificar_usuario_existente
from utils_db_mysql import guardar_historial_visual,cargar_historial_visual,eliminar_historial_visual,guardar_foro,cargar_foro,eliminar_foro
from utils_db_mysql import (
    cargar_diagnostico,
    cargar_cuestionario,
    guardar_historial_estado,
    cargar_historial_estado,
    registrar_usuario,
    verificar_usuario_existente
)
from utils_db_mysql import cargar_ultimo_historial
import plotly.graph_objects as go


crear_db()

# ===============================
# 🔥 Diccionario de Reporte de Piel
# ===============================

reporte = {
        "Grasa": {
            "descripcion": "✔️ Tu piel produce exceso de sebo ➝ tendencia a brillo, poros dilatados y acné.",
            "causas": "Hormonas, estrés, dieta alta en grasas/azúcares, genética.",
            "problemas": "Brotes, puntos negros, textura irregular, poros dilatados.",
            "advertencias": "⚠️ Prioriza limpieza adecuada. Evita aceites pesados y productos comedogénicos. Usa SPF toque seco.",
            "rutina": """
    🗓️ **Rutina Semanal Piel Grasa:**  
    ➖ Mañana:  
    - 🧼 Gel limpiador purificante.  
    - 🔬 Suero de niacinamida o ácido azelaico.  
    - 💧 Hidratante oil-free.  
    - ☀️ Protector solar toque seco.  

    ➖ Noche:  
    - 🧼 Limpieza suave.  
    - 🧪 Exfoliante BHA (2x/semana).  
    - 💧 Hidratante liviano.  
    - 🌙 Retinoides si es necesario.  
            """
        },
        "Seca": {
            "descripcion": "✔️ Tu piel produce poca grasa ➝ se siente tirante, opaca o presenta descamación.",
            "causas": "Clima, sobrelimpieza, productos agresivos, falta de hidratación.",
            "problemas": "Resequedad, descamación, líneas finas, envejecimiento prematuro.",
            "advertencias": "⚠️ Evita limpiadores fuertes. Prioriza hidratantes con lípidos, ceramidas y aceites.",
            "rutina": """
    🗓️ **Rutina Semanal Piel Seca:**  
    ➖ Mañana:  
    - 🧼 Limpiador syndet suave.  
    - 🔬 Suero de ácido hialurónico.  
    - 💧 Hidratante rico con ceramidas o manteca.  
    - ☀️ Protector solar hidratante.  

    ➖ Noche:  
    - 🧼 Limpieza suave.  
    - 💦 Mascarilla hidratante (2-3x/semana).  
    - 💧 Hidratante + aceite facial.  
            """
        },
        "Mixta": {
            "descripcion": "✔️ Zonas grasas (frente, nariz, mentón) y zonas secas (mejillas).",
            "causas": "Genética, desequilibrio en producción de sebo.",
            "problemas": "Brillo en zona T, resequedad en mejillas, brotes localizados.",
            "advertencias": "⚠️ Equilibra ➝ trata cada zona según necesidad. Hidratantes balanceados.",
            "rutina": """
    🗓️ **Rutina Semanal Piel Mixta:**  
    ➖ Mañana:  
    - 🧼 Gel limpiador balanceado.  
    - 🔬 Suero de niacinamida en zona T.  
    - 💧 Hidratante ligero.  
    - ☀️ Protector solar oil-free toque seco.  

    ➖ Noche:  
    - 🧼 Limpieza balanceada.  
    - 🧪 Mascarilla de arcilla zona T (1x/semana).  
    - 💦 Mascarilla hidratante mejillas (1x/semana).  
    - 💧 Hidratante liviano.  
            """
        },
        "Sensible": {
            "descripcion": "✔️ Tu piel reacciona fácil ➝ rojeces, picazón, ardor, sensibilidad extrema.",
            "causas": "Barrera cutánea débil, clima, estrés, productos irritantes.",
            "problemas": "Rojeces, ardor, descamación, inflamación.",
            "advertencias": "⚠️ Evita exfoliantes físicos, alcohol, fragancias, retinol sin supervisión.",
            "rutina": """
    🗓️ **Rutina Semanal Piel Sensible:**  
    ➖ Mañana:  
    - 🧼 Limpiador ultra suave sin fragancia.  
    - 💧 Hidratante con centella, pantenol o madecassoside.  
    - ☀️ Protector solar físico/mineral.  

    ➖ Noche:  
    - 🧼 Limpieza suave.  
    - 💧 Hidratante calmante intenso.  
    - 🔬 Suero calmante opcional.  
            """
        },
        "Deshidratada": {
            "descripcion": "✔️ Tu piel carece de agua ➝ sensación de tirantez, pero puede tener brillo o poros marcados.",
            "causas": "Ambientes secos, sobrelimpieza, falta de hidratación, desequilibrio de barrera.",
            "problemas": "Tirantez, líneas finas, textura áspera, poros dilatados.",
            "advertencias": "⚠️ Prioriza hidratación constante. Evita jabones agresivos y ambientes secos.",
            "rutina": """
    🗓️ **Rutina Semanal Piel Deshidratada:**  
    ➖ Mañana:  
    - 🧼 Limpiador suave.  
    - 💦 Suero ácido hialurónico.  
    - 💧 Hidratante balanceado (no pesado pero reparador).  
    - ☀️ Protector solar.  

    ➖ Noche:  
    - 🧼 Limpieza suave.  
    - 💦 Doble hidratación ➝ suero + crema.  
    - 💦 Mascarilla hidratante (2x/semana).  
            """
        },
        "Rosácea": {
            "descripcion": "✔️ Enrojecimiento crónico, vasos visibles, sensibilidad extrema. Necesita rutina muy suave.",
            "causas": "Genética, cambios de temperatura, estrés, picantes, alcohol.",
            "problemas": "Rojeces permanentes, ardor, inflamación, brotes ocasionales.",
            "advertencias": "⚠️ Evita sol, calor, alcohol, fragancias, exfoliantes fuertes.",
            "rutina": """
    🗓️ **Rutina Semanal Piel con Rosácea:**  
    ➖ Mañana:  
    - 🧼 Limpiador calmante.  
    - 💧 Hidratante con centella y ceramidas.  
    - ☀️ Protector solar mineral físico.  

    ➖ Noche:  
    - 🧼 Limpieza suave.  
    - 💧 Hidratante reparador intenso.  
    - 🔬 Suero calmante ➝ niacinamida (baja) o ácido azelaico.  
            """
        },
        "Normal": {
            "descripcion": "✔️ Tu piel está equilibrada ➝ ni exceso de grasa ni resequedad. ¡Sigue cuidándola para mantenerla sana!",
            "causas": "Genética, buen cuidado, hábitos saludables.",
            "problemas": "✔️ Ninguno relevante si se mantiene el cuidado.",
            "advertencias": "⚠️ No te confíes ➝ sigue usando protector solar y rutina básica diaria.",
            "rutina": """
    🗓️ **Rutina Semanal Piel Normal:**  
    ➖ Mañana:  
    - 🧼 Limpiador suave.  
    - 💧 Hidratante ligero.  
    - ☀️ Protector solar.  

    ➖ Noche:  
    - 🧼 Limpieza suave.  
    - 💧 Hidratación balanceada.  
    - 🔬 Suero antioxidante opcional (vitamina C o niacinamida).  
            """
        }
    }


# ===========================
# Base de usuarios
# ===========================
usuarios = {
    "demo@free.com": {"password": "1234", "tipo": "Free", "nombre": "Alvaro"},
    "demo@premium.com": {"password": "1234", "tipo": "Premium", "nombre": "Maria"}
}

# ===========================
# Frases motivadoras
# ===========================
frases = [
    "Recuerda: tu piel cuenta tu historia.",
    "Tu piel es hermosa en todas sus formas.",
    "Ama tu piel, honra tu alma.",
    "Cuidarte es un acto de amor propio.",
    "Tu belleza es única, como tu piel."
]

# ===========================
# 🔑 LOGIN Y REGISTRO
# ===========================
# ✅ Configuración de la página
st.set_page_config(page_title="Kuyay Skin", page_icon="💖")

# ✅ Variables de estado
if "registro" not in st.session_state:
    st.session_state["registro"] = False

# ===========================
# 🔐 INICIO DE SESIÓN
# ===========================
if "usuario" not in st.session_state and not st.session_state["registro"]:
    # ✅ Logo
    st.image("KuyaySkin.png", width=220)

    st.title("💖 Bienvenido a Kuyay Skin")
    st.subheader("🔑 Iniciar Sesión")

    email = st.text_input("📧 Email")
    password = st.text_input("🔑 Contraseña", type="password")

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("🚪 Iniciar Sesión"):
            if verificar_usuario_existente(email, password):
                datos = verificar_usuario_existente(email, password)
                st.session_state["usuario"] = datos[0]
                st.session_state["nombre"] = datos[1]
                st.session_state["tipo"] = datos[3]
                st.success("✅ Sesión iniciada correctamente.")
                st.rerun()
            else:
                st.error("❌ Email o contraseña incorrectos.")

    with col2:
        if st.button("📝 Crear cuenta nueva"):
            st.session_state["registro"] = True

    st.divider()

    st.info("""  
🧑‍💻 **Usuarios de prueba:**  
- demo@free.com / 1234 (Cuenta Free)  
- demo@premium.com / 1234 (Cuenta Premium)  
""")

# ===========================
# 📝 REGISTRO DE NUEVO USUARIO
# ===========================
elif st.session_state["registro"]:
    st.image("KuyaySkin.png", width=220)

    st.title("📝 Registro de Nuevo Usuario")

    nombre = st.text_input("👤 Nombre completo")
    email = st.text_input("📧 Correo electrónico")
    password = st.text_input("🔑 Crea tu contraseña", type="password")
    tipo = st.selectbox("💎 Tipo de cuenta", ["Free", "Premium"])

    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("✅ Registrarme"):
            if nombre == "" or email == "" or password == "":
                st.warning("⚠️ Todos los campos son obligatorios.")
            elif verificar_usuario_existente(email):
                st.error("🚫 Este correo ya está registrado. Intenta iniciar sesión.")
            else:
                registrar_usuario(email, nombre, password, tipo)
                st.success("✅ Registro exitoso. Ahora inicia sesión.")
                st.session_state["registro"] = False

    with col2:
        if st.button("🔙 Volver al inicio de sesión"):
            st.session_state["registro"] = False

# ===========================
# 🚀 NAVBAR + INICIO APP
# ===========================
else:
    # Menú
    if "menu" not in st.session_state:
        st.session_state["menu"] = "🏠 Inicio"

    menu = st.sidebar.selectbox(
        "Navegación",
        [
            "🏠 Inicio",
            "🔍 Diagnóstico",
            "📝 Cuestionario Dermatológico",
            "🛍️ Productos y Rutinas",
            "📚 Educación e Ingredientes",
            "🫂 Comunidad Premium",
            "🤖 Chat IA Dermatológica (Premium)",
            "🎥 Videollamada con Dermatólogo (Demo Premium)",
            "🔎 Comparador de Precios (Premium)",
            "🎁 Descuentos y Beneficios (Premium)",
            "👤 Perfil"
        ],
        index=[
            "🏠 Inicio",
            "🔍 Diagnóstico",
            "📝 Cuestionario Dermatológico",
            "🛍️ Productos y Rutinas",
            "📚 Educación e Ingredientes",
            "🫂 Comunidad Premium",
            "🤖 Chat IA Dermatológica (Premium)",
            "🎥 Videollamada con Dermatólogo (Demo Premium)",
            "🔎 Comparador de Precios (Premium)",
            "🎁 Descuentos y Beneficios (Premium)",
            "👤 Perfil"
        ].index(st.session_state["menu"])
    )

    st.session_state["menu"] = menu

    st.sidebar.title("💖 Kuyay Skin")
    st.sidebar.write(f"👤 Conectado como: {st.session_state['nombre']} ({st.session_state['tipo']})")

    if st.sidebar.button("🚪 Cerrar Sesión"):
        st.session_state.clear()
        st.rerun()


# ===========================
# 🏠 INICIO
# ===========================
    if menu == "🏠 Inicio":

        st.title(f"💖 Hola, {st.session_state['nombre']} 👋")
        st.subheader(datetime.now().strftime("📅 Hoy es %d de %B de %Y"))

        st.markdown(f"""
        ### 💡 **Consejo del día:**  
        *{random.choice(frases)}*
        """)

        st.divider()

        # ➕ Cargar datos de la base de datos
        diagnostico = cargar_diagnostico(st.session_state["usuario"])
        cuestionario = cargar_cuestionario(st.session_state["usuario"])

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🧴 Estado de tu piel")

            if diagnostico and cuestionario:
                tipo_piel = diagnostico[1]
                hidratacion = "Óptima" if cuestionario[8] == "Sí" else "Baja"
                sensibilidad = "Moderada" if cuestionario[4] == "Sí" else "Baja"
                protector = "Óptima" if cuestionario[9] == "Sí" else "Baja"

                st.info(f"✨ Tu última evaluación fue: **Piel {tipo_piel}**")

                st.markdown(f"""
                - Hidratación: {"🟢 Óptima" if hidratacion == "Óptima" else "🔴 Baja"}  
                - Sensibilidad: {"🟡 Moderada" if sensibilidad == "Moderada" else "🟢 Baja"}  
                - Protección solar: {"🟢 Óptima" if protector == "Óptima" else "🔴 Deficiente"}  
                """)

                # 🎯 Progreso de cuidado dinámico
                progreso = 0

                progreso += 25  # Por haber hecho diagnóstico y cuestionario

                if protector == "Óptima":
                    progreso += 20
                else:
                    progreso += 10

                if hidratacion == "Óptima":
                    progreso += 20
                else:
                    progreso += 10

                if sensibilidad == "Baja":
                    progreso += 20
                else:
                    progreso += 10

                progreso += 15  # Puntos base por constancia (puedes ajustar)

                progreso = min(progreso, 100)

                st.progress(progreso, text=f"Progreso de cuidado: {progreso}%")

            else:
                st.info("🔍 Aún no has realizado tu diagnóstico o cuestionario.")
                st.progress(10, text="Progreso de cuidado: 10% (Inicia tu diagnóstico)")

        with col2:
            st.subheader("🚀 Accesos rápidos")
            if st.button("🔍 Diagnóstico de piel"):
                st.session_state["menu"] = "🔍 Diagnóstico"
                st.rerun()
            if st.button("📝 Cuestionario Dermatológico"):
                st.session_state["menu"] = "📝 Cuestionario Dermatológico"
                st.rerun()
            if st.button("🛍️ Productos y Rutinas"):
                st.session_state["menu"] = "🛍️ Productos y Rutinas"
                st.rerun()
            if st.button("📚 Educación"):
                st.session_state["menu"] = "📚 Educación e Ingredientes"
                st.rerun()
            if st.session_state["tipo"] == "Premium":
                if st.button("🫂 Comunidad Premium"):
                    st.session_state["menu"] = "🫂 Comunidad Premium"
                    st.rerun()
                if st.button("🤖 Chat IA"):
                    st.session_state["menu"] = "🤖 Chat IA Dermatológica (Premium)"
                    st.rerun()

        st.divider()

        # ➕ Métricas visuales
        st.subheader("📊 Seguimiento general")

        col3, col4, col5 = st.columns(3)

        if diagnostico and cuestionario:
            col3.metric("🌞 Protección solar", protector, "✅" if protector == "Óptima" else "⚠️")
            col4.metric("💧 Hidratación", hidratacion, "✅" if hidratacion == "Óptima" else "⚠️")
            col5.metric("😌 Sensibilidad", sensibilidad, "🟡" if sensibilidad == "Moderada" else "🟢")
        else:
            col3.metric("🌞 Protección solar", "Desconocido", "⚠️")
            col4.metric("💧 Hidratación", "Desconocido", "⚠️")
            col5.metric("😌 Sensibilidad", "Desconocido", "⚠️")

        # ==========================
        # 📈 Gráfico Radar Profesional
        # ==========================
        st.divider()
        st.subheader("📈 Visualización general del estado de tu piel")

        if diagnostico and cuestionario:
            aspectos = ["Protección solar", "Hidratación", "Sensibilidad", "Constancia", "Salud general"]
            valores = [
                80 if protector == "Óptima" else 50,
                85 if hidratacion == "Óptima" else 55,
                65 if sensibilidad == "Moderada" else 40,
                70,  # Constancia (puede ser dinámica si quieres)
                75   # Salud general (promedio o se calcula después)
            ]

            fig = go.Figure()

            fig.add_trace(go.Scatterpolar(
                r=valores,
                theta=aspectos,
                fill='toself',
                name='Estado Actual',
                line_color='#00A86B'
            ))

            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100],
                        gridcolor="lightgray"
                    ),
                    bgcolor="#F9F9F9"
                ),
                showlegend=False,
                title="🌟 Evaluación general de tu piel",
                template="plotly_white"
            )

            st.plotly_chart(fig, use_container_width=True)

        else:
            st.info("🔺 Realiza tu diagnóstico y cuestionario para visualizar tu estado actual.")

        st.success("✔️ Recuerda que una rutina constante mejora la salud de tu piel día a día.")




# ✅ Estilo CSS para que las imágenes sean más elegantes
    st.markdown("""
    <style>
    img {
        border-radius: 15px;
        box-shadow: 2px 4px 10px rgba(0,0,0,0.15);
        margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# ===========================
# 🔍 DIAGNÓSTICO
# ===========================
    if menu == "🔍 Diagnóstico":
        st.title("🔍 Análisis Avanzado de Piel con IA")

        st.markdown("""
        📸 **Sube una selfie con buena iluminación, fondo neutro y sin maquillaje.**  
        ❗️ *Solo se aceptan imágenes de rostros humanos. Si subes fotos de objetos, animales o cosas no humanas te saldrá error.*  
        """)

        st.divider()

        col1, col2 = st.columns([2, 2], gap="large")

        # ===================
        # 🪞 Vista previa
        # ===================
        with col1:
            st.subheader("🪞 Vista previa:")

            imagen_subida = st.file_uploader("Selecciona tu selfie", type=["jpg", "jpeg", "png"])

            if imagen_subida is not None:
                imagen = Image.open(imagen_subida)
                st.image(imagen, caption="📷 Selfie cargada", width=280)
            else:
                st.info("🔺 Aún no has subido ninguna imagen.")

        # ===================
        # 🔬 Resultado
        # ===================
        with col2:
            st.subheader("🔬 Resultado del análisis:")

            if imagen_subida is not None:
                if st.button("🔍 Analizar imagen"):
                    if not es_rostro_valido(imagen):
                        st.error("🚫 No se detectó un rostro humano válido. Por favor, sube una selfie con tu rostro bien iluminado.")
                    else:
                        tipo_piel, descripcion = analizar_piel(imagen)

                        st.success(f"✅ Tu tipo de piel es: **{tipo_piel}**")
                        st.info(f"🧠 {descripcion}")

                        datos = reporte[tipo_piel]  # ✔️ Asegúrate que esté definido globalmente

                        st.markdown(f"""
    ### 🧠 **Descripción:**  
    {datos['descripcion']}

    ### 📚 **Causas:**  
    {datos['causas']}

    ### 🔥 **Problemas frecuentes:**  
    {datos['problemas']}

    ### ⚠️ **Advertencias:**  
    {datos['advertencias']}

    ### 📅 **Rutina semanal recomendada:**  
    {datos['rutina']}
                        """)

                        # ✔️ Guardar diagnóstico
                        guardar_diagnostico(
                            st.session_state["usuario"],
                            tipo_piel,
                            datos["descripcion"],
                            datos["causas"],
                            datos["advertencias"],
                            datos["problemas"]
                        )

                        # ✔️ Guardar en historial de estado
                        cuestionario = cargar_cuestionario(st.session_state["usuario"])

                        guardar_historial_estado(
                            st.session_state["usuario"],
                            tipo_piel,
                            hidratacion="Sí" if cuestionario and cuestionario[8] == "Sí" else "No",
                            sensibilidad="Sí" if cuestionario and cuestionario[4] == "Sí" else "No",
                            protector="Sí" if cuestionario and cuestionario[9] == "Sí" else "No"
                        )

                        st.success("💖 Diagnóstico guardado exitosamente. Lo verás reflejado en tu pantalla de inicio.")
                else:
                    st.info("👈 Da click en **Analizar imagen** para ver tu resultado.")
            else:
                st.info("⬆️ Carga una selfie para comenzar el análisis.")

# 📝 CUESTIONARIO
# ===========================
    if menu == "📝 Cuestionario Dermatológico":
        st.title("📝 Cuestionario Dermatológico")

        st.subheader("🔎 Responde para personalizar tus recomendaciones.")
        st.divider()

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("👤 Datos personales")
            edad = st.slider("📅 Edad:", 10, 70, 25)
            genero = st.selectbox("🚻 Género:", ["Femenino", "Masculino", "Otro"])
            tipo_piel = st.selectbox(
                "💆‍♀️ ¿Cómo sientes tu piel normalmente?",
                ["Grasa", "Seca", "Mixta", "Sensible", "No estoy seguro/a"]
            )

        with col2:
            st.subheader("🧠 Hábitos y condiciones")
            sensibilidad = st.radio("🌡️ ¿Tu piel suele irritarse?", ["Sí", "No"])
            acne = st.radio("💢 ¿Tienes acné, granitos o brotes?", ["Sí", "No"])
            manchas = st.radio("🌑 ¿Tienes manchas, cicatrices o hiperpigmentación?", ["Sí", "No"])
            exposicion = st.radio("☀️ ¿Estás expuesto/a al sol?", ["Sí", "No"])
            hidratacion = st.radio("💧 ¿Usas crema hidratante diariamente?", ["Sí", "No"])
            protector = st.radio("🧴 ¿Usas protector solar todos los días?", ["Sí", "No"])

        st.divider()
        st.subheader("✔️ Resultado del Cuestionario")

        if st.button("📊 Generar resultado"):
            resultado = ""

            if tipo_piel != "No estoy seguro/a":
                resultado += f"➡️ Tu piel parece ser **{tipo_piel.lower()}**.\n\n"
            else:
                resultado += "➡️ No estás seguro/a de tu tipo de piel, te sugerimos realizar un escaneo facial.\n\n"

            if sensibilidad == "Sí":
                resultado += "⚠️ Tu piel muestra signos de **sensibilidad**, usa productos calmantes.\n\n"
            if acne == "Sí":
                resultado += "💢 Presentas problemas de **acné**, usa productos no comedogénicos.\n\n"
            if manchas == "Sí":
                resultado += "🌑 Tienes manchas o cicatrices, considera tratamiento despigmentante.\n\n"
            if exposicion == "Sí":
                resultado += "☀️ Alta exposición al sol ➝ Usa protector solar diario y antioxidantes.\n\n"
            if hidratacion == "No":
                resultado += "💧 No usas hidratante ➝ Tu piel podría estar deshidratada.\n\n"
            if protector == "No":
                resultado += "⚠️ No usas protector solar ➝ Esto puede dañar tu piel a largo plazo.\n\n"

            resultado += "❤️ Recomendamos complementar este cuestionario con el **escaneo facial**."

            st.success(resultado)

            guardar_cuestionario(
                st.session_state["usuario"],
                edad, genero, tipo_piel, sensibilidad,
                acne, manchas, exposicion, hidratacion, protector
            )

            st.success("💾 Cuestionario guardado exitosamente en tu perfil.")

        else:
            st.info("👈 Completa el cuestionario y luego da click en **Generar resultado**.")


# ===========================
# 🛍️ Productos y Rutinas
# ===========================
    if menu == "🛍️ Productos y Rutinas":
        st.title("🛍️ Tu Rutina Personalizada y Productos Recomendados")

        diagnostico = cargar_diagnostico(st.session_state["usuario"])
        cuestionario = cargar_cuestionario(st.session_state["usuario"])

        if diagnostico is None or cuestionario is None:
            st.warning("⚠️ Para ver tu rutina personalizada debes completar:")
            st.markdown("- 🔍 **Diagnóstico con IA**")
            st.markdown("- 📝 **Cuestionario Dermatológico**")
            st.stop()

        st.subheader("🧠 Diagnóstico de tu piel:")
        st.markdown(f"""
        - **Tipo de piel:** {diagnostico[1]}
        - **Descripción:** {diagnostico[2]}
        - **Causas:** {diagnostico[3]}
        - **Advertencias:** {diagnostico[4]}
        - **Preguntas Frecuentes:** {diagnostico[5].replace(';', ', ')}
        - **Fecha:** {diagnostico[6]}
        """)

        st.divider()

        st.subheader("📋 Datos de tu cuestionario:")
        st.markdown(f"""
        - **Edad:** {cuestionario[1]}
        - **Género:** {cuestionario[2]}
        - **Sensibilidad:** {cuestionario[4]}
        - **Acné:** {cuestionario[5]}
        - **Manchas:** {cuestionario[6]}
        - **Exposición solar:** {cuestionario[7]}
        - **Hidratación:** {cuestionario[8]}
        - **Protector solar:** {cuestionario[9]}
        - **Fecha:** {cuestionario[10]}
        """)

        st.divider()

        # ====================================
        # 📅 Rutina Semanal Dinámica y ÚNICA
        # ====================================
        st.subheader("📅 Tu Rutina Semanal (100% Personalizada)")


        tipo_piel = diagnostico[1]
        sensibilidad = cuestionario[4]
        acne = cuestionario[5]
        manchas = cuestionario[6]

        horarios = ["7:00 am", "8:00 am", "12:00 pm", "4:00 pm", "8:00 pm", "10:00 pm"]
        dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

        # Función generadora de rutina dinámica
        def generar_rutina_dinamica(dia):
            base_morning = [
                "Beber agua + afirmación positiva 💧",
                "🧼 Limpieza suave + 💧 Hidratación + ☀️ Protector solar",
                "☀️ Reaplicar protector + bruma hidratante"
            ]

            base_evening = [
                "🧼 Limpieza nocturna + 💧 Hidratación + Suero específico",
                "🌙 Relajación: respiración profunda o 5 minutos de meditación"
            ]

            extra = []

            # Agrega según condiciones
            if tipo_piel == "Grasa":
                extra.append(random.choice([
                    "✨ Suero de niacinamida",
                    "🌿 Mascarilla de arcilla (zona T) - solo si es " + random.choice(["Miércoles", "Sábado"]),
                    "💊 Retinoides (noche) - 2x/sem"
                ]))
            elif tipo_piel == "Seca":
                extra.append(random.choice([
                    "💦 Mascarilla hidratante (noche)",
                    "🌸 Aceite facial nutritivo",
                    "💧 Doble hidratación noche"
                ]))
            elif tipo_piel == "Mixta":
                extra.append(random.choice([
                    "🧪 Mascarilla de arcilla (zona T) + Hidratante zonas secas",
                    "✨ Suero balanceador",
                    "💧 Doble hidratación nocturna"
                ]))
            elif tipo_piel == "Sensible":
                extra.append(random.choice([
                    "🧴 Hidratante calmante con centella",
                    "🌿 Suero reparador con madecassoside",
                    "🚫 Evitar exfoliantes hoy"
                ]))
            elif tipo_piel == "Deshidratada":
                extra.append(random.choice([
                    "💧 Mascarilla hidratante nocturna",
                    "✨ Doble suero (ácido hialurónico + niacinamida)",
                    "🌿 Hidratante + bruma durante el día"
                ]))
            elif tipo_piel == "Rosácea":
                extra.append(random.choice([
                    "🧴 Hidratante anti-rojeces con centella",
                    "💧 Refuerzo de hidratación x3",
                    "☁️ Evitar calor y picantes este día"
                ]))
            elif tipo_piel == "Normal":
                extra.append(random.choice([
                    "💧 Hidratación balanceada",
                    "✨ Suero antioxidante (Vitamina C o Niacinamida)",
                    "🌸 Mascarilla nutritiva ligera"
                ]))

            # Si hay sensibilidad o manchas o acné, personalizar más
            if sensibilidad == "Sí":
                extra.append("🚫 Cuidado con productos irritantes hoy")
            if acne == "Sí":
                extra.append("💢 Aplicar tratamiento anti-acné puntual")
            if manchas == "Sí":
                extra.append("🌑 Usar suero despigmentante noche")

            rutina = {
                "7:00 am": base_morning[0],
                "8:00 am": base_morning[1],
                "12:00 pm": base_morning[2],
                "4:00 pm": "☀️ Reaplicar protector + agua micelar (si hubo sudor)",
                "8:00 pm": base_evening[0],
                "10:00 pm": random.choice(extra) + " + " + base_evening[1]
            }

            return rutina

        data_rutina = {dia: list(generar_rutina_dinamica(dia).values()) for dia in dias}

        df = pd.DataFrame(data_rutina, index=horarios)

        st.dataframe(df, use_container_width=True)

        st.success("✨ Tu rutina ha sido generada ➝ ÚNICA y personalizada por días y horarios.")

        st.divider()

        # =========================
        # 🛍️ Productos recomendados
        # =========================
        st.subheader("🛍️ Productos recomendados para ti:")

        productos = {
            "Grasa": [
                {"nombre": "Gel Limpiador La Roche-Posay", "precio": "S/.79", "link": "https://mercadolibre.com.pe"},
                {"nombre": "Hidratante Cetaphil Oil-Free", "precio": "S/.55", "link": "https://inkafarma.pe"},
                {"nombre": "Protector Solar ISDIN Fusion Water", "precio": "S/.95", "link": "https://inkafarma.pe"}
            ],
            "Seca": [
                {"nombre": "CeraVe Limpiador Hidratante", "precio": "S/.70", "link": "https://mercadolibre.com.pe"},
                {"nombre": "Neutrogena Hydro Boost Crema", "precio": "S/.60", "link": "https://inkafarma.pe"},
                {"nombre": "La Roche-Posay Anthelios SPF Hidratante", "precio": "S/.98", "link": "https://inkafarma.pe"}
            ],
            "Mixta": [
                {"nombre": "Gel Limpiador Simple", "precio": "S/.40", "link": "https://mercadolibre.com.pe"},
                {"nombre": "Hidratante Eucerin Balance", "precio": "S/.65", "link": "https://inkafarma.pe"},
                {"nombre": "Protector Solar Umbrella Gel", "precio": "S/.70", "link": "https://inkafarma.pe"}
            ],
            "Sensible": [
                {"nombre": "Sensibio Gel Moussant", "precio": "S/.75", "link": "https://mercadolibre.com.pe"},
                {"nombre": "Hidratante La Roche-Posay Toleriane", "precio": "S/.85", "link": "https://inkafarma.pe"},
                {"nombre": "Protector Solar ISDIN Mineral", "precio": "S/.99", "link": "https://inkafarma.pe"}
            ],
            "Deshidratada": [
                {"nombre": "Limpiador Bioderma Hydrabio", "precio": "S/.80", "link": "https://mercadolibre.com.pe"},
                {"nombre": "Hidratante Clinique Moisture Surge", "precio": "S/.110", "link": "https://inkafarma.pe"},
                {"nombre": "Protector Solar Eucerin Hydro", "precio": "S/.95", "link": "https://inkafarma.pe"}
            ],
            "Rosácea": [
                {"nombre": "Sensibio DS+", "precio": "S/.85", "link": "https://mercadolibre.com.pe"},
                {"nombre": "Hidratante La Roche-Posay Rosaliac", "precio": "S/.105", "link": "https://inkafarma.pe"},
                {"nombre": "Protector Solar ISDIN Mineral", "precio": "S/.99", "link": "https://inkafarma.pe"}
            ],
            "Normal": [
                {"nombre": "CeraVe Gel Espumoso", "precio": "S/.65", "link": "https://mercadolibre.com.pe"},
                {"nombre": "Neutrogena Hydro Boost", "precio": "S/.60", "link": "https://inkafarma.pe"},
                {"nombre": "ISDIN Fusion Water", "precio": "S/.95", "link": "https://inkafarma.pe"}
            ]
        }

        tipo = tipo_piel if tipo_piel in productos else "Normal"
        for item in productos[tipo]:
            st.markdown(f"""
            🏬 **{item['nombre']}**  
            💰 {item['precio']}  
            🔗 [Ver producto]({item['link']})
            """)

        st.success("💖 Tu rutina y tus productos están listos.")


# ==========================
# 📚 EDUCACIÓN
# ===========================
    if menu == "📚 Educación e Ingredientes":
        st.title("📚 Educación en SkinCare")

        st.subheader("🧠 Aprende sobre tu piel de forma fácil y visual:")

        st.divider()

        tema = st.selectbox(
            "🔎 Selecciona un tema para aprender más:",
            ["Acné", "Barrera cutánea", "pH de la piel", "Ingredientes cosméticos", "Autoestima y cuidado emocional (Premium)"]
        )

        st.divider()

        col1, col2 = st.columns([1, 2])

        with col1:
            st.image("https://cdn-icons-png.flaticon.com/512/3771/3771572.png", width=180)  # Icono educativo decorativo

        with col2:
            if tema == "Acné":
                st.subheader("🔬 ¿Qué es el acné?")
                st.markdown("""
                El acné es una afección de la piel que ocurre cuando los folículos pilosos se obstruyen con sebo y células muertas.

                **⚠️ Factores:**  
                - Exceso de sebo  
                - Cambios hormonales  
                - Estrés y dieta  

                **💡 Recomendaciones:**  
                - 🧼 Limpieza suave dos veces al día.  
                - 🧴 Usa productos no comedogénicos.  
                - ☀️ Usa protector solar siempre.
                """)

            elif tema == "Barrera cutánea":
                st.subheader("🧪 ¿Qué es la barrera cutánea?")
                st.markdown("""
                Es la capa externa de la piel que protege de bacterias, contaminación y evita la pérdida de agua.

                **😥 Cuando está dañada:**  
                - Piel roja, seca, con ardor o descamación.  

                **🔧 Cómo repararla:**  
                - Hidratantes con ceramidas o ácido hialurónico.  
                - Evitar limpiadores agresivos.  
                - Uso constante de protector solar.
                """)

            elif tema == "pH de la piel":
                st.subheader("⚗️ ¿Qué es el pH de la piel?")
                st.markdown("""
                El pH mide la acidez de tu piel. Un pH saludable es **4.5 a 5.5**, ligeramente ácido.

                **🛑 Si se altera:**  
                - Brotes, sensibilidad y resequedad aumentan.

                **✔️ Cómo mantenerlo:**  
                - Limpiadores suaves (syndet).  
                - Evitar jabones alcalinos.  
                - Hidratación diaria.
                """)

            elif tema == "Ingredientes cosméticos":
                st.subheader("🧴 Ingredientes claves en tu rutina:")
                st.markdown("""
                - **AHA (Ácido Glicólico, Láctico):** Exfoliación química, mejora textura y manchas.  
                - **BHA (Ácido Salicílico):** Limpieza de poros, ideal para acné.  
                - **Niacinamida:** Controla grasa, calma la piel y mejora manchas.  
                - **Ceramidas:** Reparan la barrera cutánea.  
                - **Ácido Hialurónico:** Hidratación intensa.  
                - **Retinol:** Mejora arrugas, textura, manchas (uso nocturno).  
                - **Vitamina C:** Antioxidante, aclara manchas y da luminosidad.

                ⚠️ Siempre revisa si tu piel tolera estos activos y combínalos adecuadamente.
                """)

            elif tema == "Autoestima y cuidado emocional (Premium)":
                if st.session_state["tipo"] == "Premium":
                    st.subheader("💖 Autoestima y cuidado emocional")
                    st.markdown("""
                    Cuidar tu piel es también cuidar tu mente y tu bienestar emocional.

                    - ✨ Recuerda: **Tu piel no te define.**  
                    - No te compares, tu proceso es único.  
                    - Los brotes, manchas o textura no te hacen menos.  
                    - Amar tu piel es un acto de amor propio, no de perfección.  

                    **🧠 Prácticas recomendadas:**  
                    - Afirmaciones diarias: *"Mi piel está mejorando cada día."*  
                    - Registra tus avances y celébralos.  
                    - Dedica tiempo al autocuidado sin juzgarte.  
                    - Cuida tu salud mental tanto como la física.
                    """)
                else:
                    st.warning("🚫 Este contenido es exclusivo para usuarios Premium.")

# ===========================
# 🫂 COMUNIDAD
# ===========================
    if menu == "🫂 Comunidad Premium":
        if st.session_state["tipo"] == "Premium":
            st.title("🫂 Comunidad Kuyay Premium")

            st.subheader("📸 Mi Historial Visual de Piel")
            st.info("Sube fotos periódicas para llevar el registro de tu progreso y ver cómo mejora tu piel con el tiempo.")

            st.divider()

            # =======================
            # 🗓️ Historial Visual
            # =======================
            st.subheader("🗓️ Mi historial visual:")

            foto = st.file_uploader("📤 Sube una foto de tu piel (Selfie o zona a analizar)", type=["jpg", "jpeg", "png"])

            if st.button("➕ Agregar al historial") and foto is not None:
                guardar_historial_visual(st.session_state["usuario"], foto.read())
                st.success("✅ Foto agregada exitosamente.")

            historial = cargar_historial_visual(st.session_state["usuario"])

            if historial:
                for id_foto, imagen_bytes, fecha in historial:
                    st.markdown(f"**📅 {fecha.strftime('%d-%m-%Y %H:%M')}**")
                    st.image(imagen_bytes, width=300)
                    if st.button(f"🗑️ Eliminar foto {id_foto}"):
                        eliminar_historial_visual(id_foto)
                        st.success("✅ Foto eliminada correctamente.")
                        st.rerun()
                    st.divider()
            else:
                st.info("🔺 Aún no tienes fotos en tu historial.")

            st.markdown("""
            ### 💡 Tips para tu historial:
            - 📷 Sube una foto semanalmente.  
            - 📅 Mantén la misma luz y ángulo.  
            - 🔍 Úsalo para ver mejoras reales en tu piel.  
            """)

            st.divider()

            # =======================
            # 📝 Foro de la Comunidad
            # =======================
            st.subheader("💬 Foro de la Comunidad")

            categoria = st.selectbox(
                "📂 Elige una categoría para tu post:",
                ["General", "Dudas sobre productos", "Avances de mi piel", "Recomendaciones", "Otros"]
            )

            comentario = st.text_area("✍️ Escribe tu comentario, duda o experiencia:")

            imagen_post = st.file_uploader("📸 (Opcional) Sube una imagen para tu publicación:", type=["jpg", "jpeg", "png"])

            if st.button("📤 Publicar comentario"):
                if comentario.strip() != "":
                    imagen_bytes = imagen_post.read() if imagen_post is not None else None
                    guardar_foro(st.session_state["usuario"], st.session_state["nombre"], categoria, comentario, imagen_bytes)
                    st.success("✅ Comentario publicado.")
                    st.rerun()
                else:
                    st.warning("⚠️ El comentario no puede estar vacío.")

            st.divider()

            st.subheader("📜 Publicaciones del foro:")

            foro = cargar_foro()

            if foro:
                for id_post, nombre_usuario, categoria, texto, imagen_bytes, fecha in foro:
                    st.markdown(f"""
                    🏷️ **Categoría:** {categoria}  
                    **{nombre_usuario}** 🕓 *{fecha.strftime('%d-%m-%Y %H:%M')}*  
                    > {texto}
                    """)
                    if imagen_bytes:
                        st.image(imagen_bytes, width=300)

                    if st.session_state["usuario"] == foro[id_post-1][1]:  # Solo si es el dueño puede eliminar
                        if st.button(f"🗑️ Eliminar publicación {id_post}"):
                            eliminar_foro(id_post)
                            st.success("✅ Publicación eliminada.")
                            st.rerun()

                    st.divider()
            else:
                st.info("🪴 Aún no hay publicaciones en el foro. Sé el primero en compartir tu experiencia o duda.")
        else:
            st.warning("🚫 Esta sección es solo para usuarios Premium.")



    # ===========================
    # 🤖 CHAT IA
    # ===========================
    if menu == "🤖 Chat IA Dermatológica (Premium)":
        if st.session_state["tipo"] == "Premium":
            st.title("🤖 Chat IA Dermatológica 24/7")

            st.subheader("💬 Soy KuyayBot, tu asistente de skincare. Pregúntame sobre acné, manchas, hidratación, barrera cutánea, sensibilidad, pH, rutinas o ingredientes.")

            if "chat" not in st.session_state:
                st.session_state["chat"] = []

            user_input = st.text_input("✍️ Tú:")

            if st.button("Enviar") and user_input.strip() != "":
                st.session_state["chat"].append({"usuario": "Tú", "mensaje": user_input})

                pregunta = user_input.lower()

                respuesta = ""

                # 🔥 Detecta preguntas generales como "Qué me recomiendas"
                if any(p in pregunta for p in ["qué me recomiendas", "qué puedo hacer", "me ayudas", "qué hago"]):
                    respuesta += "🩺 Claro, dime si tu duda es sobre acné, manchas, hidratación, sensibilidad, barrera cutánea, pH o ingredientes. ✔️ Escríbelo y te daré una guía completa.\n\n"

                # 🔥 Acné
                if any(p in pregunta for p in ["acné", "granitos", "espinillas", "brotes"]):
                    respuesta += """
    💢 **Acné - Guía completa:**  
    ✔️ **Rutina:**  
    1️⃣ Limpieza ➝ gel sin sulfatos (mañana y noche).  
    2️⃣ Hidratación ➝ con niacinamida, ácido hialurónico o pantenol.  
    3️⃣ Tratamiento ➝ ácido salicílico (BHA) o peróxido de benzoilo. ➝ Noche: adapaleno o retinoides.  
    4️⃣ Protector solar ➝ oil-free, toque seco, reaplicar cada 3 horas.  

    ✔️ **Hábitos:**  
    - NO manipules granos.  
    - Cambia fundas cada 3-4 días.  
    - Reduce azúcar, leche y ultraprocesados.  

    ✔️ **Activos:**  
    - BHA ➝ Poros y brotes.  
    - Niacinamida ➝ Calmante y controla grasa.  
    - Retinoides ➝ Antiacné, manchas, textura.  

    ⏳ *Resultados desde 6-8 semanas con constancia.*  
    """

                # 🔥 Manchas
                if any(p in pregunta for p in ["manchas", "melasma", "hiperpigmentación", "cicatrices"]):
                    respuesta += """
    🌟 **Tratamiento de Manchas:**  
    ✔️ **Rutina:**  
    1️⃣ Mañana ➝ Limpieza, suero antioxidante (Vitamina C o Niacinamida), hidratante, SPF 50.  
    2️⃣ Noche ➝ Limpieza, suero despigmentante (Ácido Tranexámico, Azelaico, Kójico o Retinol), hidratante.  

    ✔️ **Activos:**  
    - Vitamina C ➝ Luminosidad y antioxidante.  
    - Niacinamida ➝ Manchas, sebo, calma.  
    - Ácido Azelaico ➝ Manchas + acné + rosácea.  
    - Retinoides ➝ Manchas + textura + acné.  

    ☀️ **Regla de oro:** SIN PROTECTOR SOLAR ➝ ninguna mancha mejora.  
    """

                # 🔥 Hidratación
                if any(p in pregunta for p in ["hidratar", "hidratante", "hidratación", "deshidratada"]):
                    respuesta += """
    💧 **Rutina para piel deshidratada:**  
    - ✅ Limpieza suave (sin sulfatos).  
    - ✅ Hidratante con Ácido Hialurónico, Ceramidas y Pantenol.  
    - ✅ SPF 50 ➝ siempre.  
    - 🌙 Noche ➝ doble hidratación o mascarilla hidratante.  

    ✔️ **Ingredientes top:**  
    - Ácido Hialurónico ➝ Hidratante.  
    - Ceramidas ➝ Reparación.  
    - Pantenol ➝ Calmante.  
    - Glicerina ➝ Atrae y retiene humedad.  
    """

                # 🔥 Sensibilidad
                if any(p in pregunta for p in ["sensibilidad", "piel sensible", "irritación", "rojeces"]):
                    respuesta += """
    🩹 **Rutina para piel sensible:**  
    1️⃣ Limpieza ultra suave, sin fragancia.  
    2️⃣ Hidratante ➝ Ceramidas, Centella Asiática, Pantenol, Avena.  
    3️⃣ SPF mineral (óxido de zinc o dióxido de titanio).  
    4️⃣ 🌙 Noche ➝ Hidratación intensa, sin exfoliantes ni retinoides hasta reparar.  

    ✔️ **Evita:** Alcohol, aceites esenciales, fragancias, exfoliantes físicos.  
    """

                # 🔥 Barrera cutánea
                if any(p in pregunta for p in ["barrera", "daño barrera", "reparar piel"]):
                    respuesta += """
    🧪 **Barrera Cutánea dañada:**  
    ✔️ **Síntomas:** Ardor, descamación, resequedad, sensibilidad extrema.  
    ✔️ **Reparación:**  
    - Limpieza muy suave.  
    - Hidratación ➝ Ceramidas + Pantenol + Ácido Hialurónico.  
    - Suspender ➝ AHA, BHA, retinol, vitamina C, exfoliantes.  
    - SPF mineral ➝ siempre.  

    ⏳ *Recuperación: 2 a 4 semanas si eres constante.*  
    """

                # 🔥 pH
                if "ph" in pregunta:
                    respuesta += """
    ⚗️ **pH de la piel:**  
    ✔️ Saludable entre 4.5 y 5.5 (ácido).  
    ✔️ Mantiene bacterias buenas, controla acné, sensibilidad y deshidratación.  

    👉 Cómo mantenerlo:  
    - Limpiadores syndet (sin jabón).  
    - Hidratación constante.  
    - Protector solar diario.  
    """

                # 🔥 Ingredientes
                if any(p in pregunta for p in ["ingredientes", "activos", "qué es", "qué hace"]):
                    respuesta += """
    🧴 **Guía de ingredientes:**  
    - **AHA (Ácido glicólico):** Textura, manchas.  
    - **BHA (Ácido salicílico):** Poros, acné.  
    - **Niacinamida:** Calma, controla grasa, aclara manchas.  
    - **Ácido Hialurónico:** Hidratación profunda.  
    - **Ceramidas:** Reparación barrera cutánea.  
    - **Retinoides:** Acné, textura, manchas, arrugas.  
    - **Vitamina C:** Antioxidante, despigmentante.  
    - **Ácido Azelaico:** Manchas, acné, rosácea.  
    """

                # 🔒 Pregunta fuera de tema
                if respuesta.strip() == "":
                    respuesta = """
    ⚠️ Soy un asistente dermatológico, solo puedo ayudarte con temas de cuidado de la piel:  
    - Acné  
    - Manchas  
    - Hidratación  
    - Sensibilidad  
    - Barrera cutánea  
    - pH de la piel  
    - Ingredientes y activos  
    - Rutinas y protección solar  

    🚫 No estoy entrenado para deportes, política, comida, farándula, etc.  
    """

                st.session_state["chat"].append({"usuario": "KuyayBot", "mensaje": respuesta})

            st.subheader("🗨️ Conversación:")

            if st.session_state["chat"]:
                for mensaje in st.session_state["chat"]:
                    if mensaje["usuario"] == "Tú":
                        st.markdown(f"**Tú:** {mensaje['mensaje']}")
                    else:
                        st.markdown(f"**KuyayBot:** {mensaje['mensaje']}")
                    st.divider()

            if st.button("🗑️ Borrar conversación"):
                st.session_state["chat"] = []
                st.rerun()  # 🔥 ✅ FUNCIONAL con versión 1.46.1
        else:
            st.warning("🚫 Esta sección es solo para usuarios Premium.")

    # ===========================
    # 🎥 COMPARADOR
    # ===========================
    if menu == "🔎 Comparador de Precios (Premium)":
        if st.session_state["tipo"] == "Premium":
            st.title("🔎 Comparador de Precios de Productos de Skincare")

            st.subheader("Selecciona el producto que deseas comparar:")

            producto_seleccionado = st.selectbox(
                "🛍️ Producto:",
                [
                    "Gel limpiador",
                    "Hidratante facial",
                    "Protector solar",
                    "Sérum de Niacinamida",
                    "Ácido Hialurónico",
                    "Suero de Vitamina C",
                    "Retinol (Uso nocturno)"
                ]
            )

            st.subheader(f"💸 Precios disponibles para: **{producto_seleccionado}**")

            # ==============================
            # Base de datos de precios + info
            # ==============================
            datos = {
                "Gel limpiador": {
                    "info": "Limpieza diaria para remover sebo e impurezas. Ideal para piel grasa, mixta o sensible.",
                    "recomendacion": "Usa 2 veces al día, mañana y noche.",
                    "precios": [
                        {"tienda": "Mercado Libre", "precio": 75, "link": "https://mercadolibre.com.pe"},
                        {"tienda": "Inkafarma", "precio": 79, "link": "https://inkafarma.pe"},
                        {"tienda": "MiFarma", "precio": 82, "link": "https://mifarma.pe"}
                    ]
                },
                "Hidratante facial": {
                    "info": "Hidrata y refuerza la barrera cutánea. Apto para todo tipo de piel, incluso grasa.",
                    "recomendacion": "Aplícalo siempre después de la limpieza y antes del protector solar.",
                    "precios": [
                        {"tienda": "Mercado Libre", "precio": 55, "link": "https://mercadolibre.com.pe"},
                        {"tienda": "Inkafarma", "precio": 60, "link": "https://inkafarma.pe"},
                        {"tienda": "MiFarma", "precio": 58, "link": "https://mifarma.pe"}
                    ]
                },
                "Protector solar": {
                    "info": "El producto más importante del skincare. Protege contra el daño solar, manchas y envejecimiento.",
                    "recomendacion": "Aplícalo cada 2-3 horas, incluso en interiores.",
                    "precios": [
                        {"tienda": "Mercado Libre", "precio": 95, "link": "https://mercadolibre.com.pe"},
                        {"tienda": "Inkafarma", "precio": 98, "link": "https://inkafarma.pe"},
                        {"tienda": "MiFarma", "precio": 97, "link": "https://mifarma.pe"}
                    ]
                },
                "Sérum de Niacinamida": {
                    "info": "Controla grasa, reduce brotes, mejora manchas y fortalece la barrera cutánea.",
                    "recomendacion": "Aplica después de la limpieza y antes del hidratante. Ideal mañana y noche.",
                    "precios": [
                        {"tienda": "Mercado Libre", "precio": 65, "link": "https://mercadolibre.com.pe"},
                        {"tienda": "Inkafarma", "precio": 70, "link": "https://inkafarma.pe"},
                        {"tienda": "MiFarma", "precio": 68, "link": "https://mifarma.pe"}
                    ]
                },
                "Ácido Hialurónico": {
                    "info": "Atrapa la humedad en tu piel, da efecto de relleno inmediato. Hidratación profunda.",
                    "recomendacion": "Aplicar sobre piel húmeda, después de la limpieza y antes del hidratante.",
                    "precios": [
                        {"tienda": "Mercado Libre", "precio": 72, "link": "https://mercadolibre.com.pe"},
                        {"tienda": "Inkafarma", "precio": 76, "link": "https://inkafarma.pe"},
                        {"tienda": "MiFarma", "precio": 75, "link": "https://mifarma.pe"}
                    ]
                },
                "Suero de Vitamina C": {
                    "info": "Antioxidante, ilumina, combate manchas y protege del envejecimiento.",
                    "recomendacion": "Usar en la mañana antes del hidratante y protector solar.",
                    "precios": [
                        {"tienda": "Mercado Libre", "precio": 80, "link": "https://mercadolibre.com.pe"},
                        {"tienda": "Inkafarma", "precio": 85, "link": "https://inkafarma.pe"},
                        {"tienda": "MiFarma", "precio": 83, "link": "https://mifarma.pe"}
                    ]
                },
                "Retinol (Uso nocturno)": {
                    "info": "Mejora textura, manchas, líneas de expresión y acné. Activo antiedad por excelencia.",
                    "recomendacion": "Usar de noche, comenzar 2-3 veces por semana e ir aumentando según tolerancia. Siempre usar protector solar al día siguiente.",
                    "precios": [
                        {"tienda": "Mercado Libre", "precio": 95, "link": "https://mercadolibre.com.pe"},
                        {"tienda": "Inkafarma", "precio": 102, "link": "https://inkafarma.pe"},
                        {"tienda": "MiFarma", "precio": 100, "link": "https://mifarma.pe"}
                    ]
                },
            }

            precios = [item["precio"] for item in datos[producto_seleccionado]["precios"]]
            precio_minimo = min(precios)

            st.markdown(f"""
            ### 📝 Descripción del producto:  
            {datos[producto_seleccionado]['info']}

            **💡 Recomendación de uso:** {datos[producto_seleccionado]['recomendacion']}
            """)

            st.divider()

            for item in datos[producto_seleccionado]["precios"]:
                es_mas_barato = item["precio"] == precio_minimo

                if es_mas_barato:
                    st.markdown(f"""
                    <div style="border: 2px solid #cccccc; border-radius: 12px; padding: 10px;">
                    🏆 <b>Mejor precio disponible</b>  
                    🏬 <b>{item['tienda']}</b><br>  
                    💰 <b>S/. {item['precio']}</b><br>  
                    🔗 <a href="{item['link']}" target="_blank">Ver producto aquí</a>  
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="border: 1px solid #cccccc; border-radius: 12px; padding: 10px;">
                    🏬 <b>{item['tienda']}</b><br>  
                    💰 <b>S/. {item['precio']}</b><br>  
                    🔗 <a href="{item['link']}" target="_blank">Ver producto aquí</a>  
                    </div>
                    """, unsafe_allow_html=True)

            st.info("ℹ️ Los precios son referenciales y pueden variar según la tienda. Verifica stock antes de comprar.")

        else:
            st.warning("🚫 Esta sección es solo para usuarios Premium.")




    
    # ===========================
    # 🎥 VIDEOLLAMADA
    # ===========================
    if menu == "🎥 Videollamada con Dermatólogo (Demo Premium)":
        if st.session_state["tipo"] == "Premium":
            st.title("🎥 Consultas Dermatológicas por Videollamada (Demo Premium)")

            st.markdown("""
            🩺 **Agenda tu cita dermatológica online de manera rápida y segura.**  
            ✔️ Accede a especialistas en cuidado de la piel desde tu casa.  
            ✔️ Resuelve dudas sobre acné, manchas, sensibilidad, productos, rutinas o tratamientos.  
            ✔️ Tu salud dermatológica, sin salir de casa.  
            """)

            st.divider()

            st.subheader("📅 **Agendar una cita:**")

            fecha = st.date_input("🗓️ Selecciona la fecha de tu cita:")
            hora = st.selectbox(
                "⏰ Selecciona el horario disponible:",
                ["10:00 AM", "11:00 AM", "3:00 PM", "4:00 PM", "5:00 PM"]
            )

            motivo = st.text_area(
                "📝 Describe el motivo de tu consulta (Ejemplo: tratamiento para acné, manchas, sensibilidad, revisión de rutina, etc.):"
            )

            if "cita_reservada" not in st.session_state:
                st.session_state["cita_reservada"] = False

            if st.button("📥 Confirmar reserva"):
                if motivo.strip() != "":
                    st.session_state["cita_reservada"] = True
                    st.success(f"""
                    ✅ Tu cita ha sido agendada exitosamente.  
                    📅 Fecha: **{fecha.strftime('%d-%m-%Y')}**  
                    ⏰ Hora: **{hora}**  
                    ✍️ Motivo: {motivo}  

                    🔔 Recuerda conectarte 5 minutos antes. El enlace aparecerá aquí el día de la cita.
                    """)
                else:
                    st.warning("⚠️ Por favor, describe el motivo de tu consulta para continuar.")

            if st.session_state["cita_reservada"]:
                st.divider()

                st.subheader("🔗 **Acceso a tu videollamada (Demo):**")

                st.markdown("""
                👉 [🟢 Ingresar a la videollamada (DEMO)](https://meet.google.com/)  

                ℹ️ Este enlace es un ejemplo para demostración. En una versión real, aquí iría el enlace a la sesión con tu dermatólogo (Google Meet, Zoom o plataforma integrada).
                """)

                st.info("""
                ✔️ **Recomendaciones para la consulta:**  
                - Conéctate desde un lugar con buena luz natural.  
                - Ten a la mano tu historial dermatológico, productos que usas y fotos recientes de tu piel.  
                - Asegúrate de tener buena conexión a internet.  
                - La consulta tiene una duración aproximada de **20 a 30 minutos.**  
                """)

                if st.button("❌ Cancelar cita"):
                    st.session_state["cita_reservada"] = False
                    st.success("🗑️ Tu cita ha sido cancelada exitosamente.")

            st.divider()

            st.subheader("❓ **¿Qué se puede consultar en una videollamada?**")
            st.markdown("""
            ✅ Evaluación de condiciones como:  
            - Acné  
            - Manchas (hiperpigmentación, melasma)  
            - Piel sensible, rosácea, dermatitis  
            - Sequedad, deshidratación o exceso de grasa  
            - Recomendación y ajuste de rutinas de skincare  

            ✅ También puedes:  
            - Revisar los productos que usas actualmente.  
            - Consultar tratamientos para cicatrices, barrera cutánea, pH alterado, etc.  
            - Obtener una rutina personalizada según tu clima, estilo de vida y necesidades.  

            🚨 **No se realizan diagnósticos médicos complejos ni se recetan medicamentos controlados en esta demo.**
            """)

        else:
            st.warning("🚫 Esta sección es exclusiva para usuarios Premium.")



    # ===========================
    # 🎁 DESCUENTOS
    # ===========================
    if menu == "🎁 Descuentos y Beneficios (Premium)":
        if st.session_state["tipo"] == "Premium":
            st.title("🎁 Beneficios y Descuentos Exclusivos de Kuyay Skin")

            st.markdown("""
            🛍️ **Disfruta de descuentos, cupones y muestras gratis solo por ser parte de la comunidad Premium de Kuyay Skin.**  
            ✔️ Ahorra en tus productos favoritos y descubre nuevos aliados para tu piel.  
            ✔️ Beneficios de marcas confiables dermatológicas y aliadas locales.
            """)

            st.divider()

            st.subheader("🎟️ **Cupones y Promociones activas:**")

            beneficios = [
                {
                    "tienda": "Inkafarma",
                    "beneficio": "10% de descuento en protectores solares de La Roche-Posay, ISDIN y Umbrella.",
                    "codigo": "KUYAY10",
                    "valido": "Hasta el 31/12/2025",
                    "condiciones": "Aplica solo en compras online. No acumulable con otras ofertas.",
                    "link": "https://inkafarma.pe"
                },
                {
                    "tienda": "Mercado Libre",
                    "beneficio": "15% de descuento en hidratantes seleccionados (CeraVe, Cetaphil, Neutrogena).",
                    "codigo": "KUYAY15",
                    "valido": "Válido durante el mes de lanzamiento.",
                    "condiciones": "Solo en productos de vendedores oficiales.",
                    "link": "https://mercadolibre.com.pe"
                },
                {
                    "tienda": "MiFarma",
                    "beneficio": "🚚 Envío gratis en compras mayores a S/.100 en la categoría dermatológica.",
                    "codigo": "ENVIOFREE",
                    "valido": "Sin fecha de caducidad mientras seas Premium.",
                    "condiciones": "Aplicable solo a Lima Metropolitana y Callao.",
                    "link": "https://mifarma.pe"
                },
                {
                    "tienda": "Laboratorio Dermato Perú",
                    "beneficio": "🎁 Muestra gratuita de suero de Niacinamida (5ml) en tu próxima compra.",
                    "codigo": "MUESTRA",
                    "valido": "Hasta agotar stock (500 unidades disponibles).",
                    "condiciones": "Una muestra por usuario Premium. No acumulable.",
                    "link": "https://laboratoriodermato.pe"
                },
                {
                    "tienda": "Aliado Local — Skincare Natural Perú",
                    "beneficio": "20% de descuento en productos veganos, cruelty-free y aptos para piel sensible.",
                    "codigo": "SKIN20",
                    "valido": "Válido hasta el 15/01/2026",
                    "condiciones": "No aplica en packs promocionales.",
                    "link": "https://skincarenaturalperu.pe"
                }
            ]

            for item in beneficios:
                st.markdown(f"""
                <div style="border:1px solid #cccccc; border-radius:12px; padding:10px;">
                🏬 <b>{item['tienda']}</b><br>  
                🎁 <b>Beneficio:</b> {item['beneficio']}<br>  
                🔑 <b>Código:</b> <code>{item['codigo']}</code><br>  
                📅 <b>Válido:</b> {item['valido']}<br>  
                📜 <b>Condiciones:</b> {item['condiciones']}<br>  
                🔗 <a href="{item['link']}" target="_blank">👉 Ir a la tienda</a>  
                </div>
                """, unsafe_allow_html=True)
                st.divider()

            st.subheader("ℹ️ **Importante:**")
            st.markdown("""
            - Estos beneficios son **exclusivos para usuarios Premium de Kuyay Skin.**  
            - Revisa la fecha de validez y las condiciones específicas de cada tienda.  
            - Los códigos son personales, no transferibles y no acumulables con otras promociones.  
            - **Actualizamos los beneficios mensualmente.**  
            """)

        else:
            st.warning("🚫 Esta sección es solo para usuarios Premium.")



    # ===========================
    # 👤 PERFIL
    # ===========================
    if menu == "👤 Perfil":
        st.title("👤 Mi Perfil")

        st.markdown("""
        🧑‍💻 **Aquí puedes ver y gestionar tu información de cuenta.**  
        ✔️ Revisa tus datos, tu tipo de suscripción y tu historial dentro de Kuyay Skin.  
        """)

        st.divider()

        # Información de usuario
        nombre = st.session_state["nombre"]
        email = st.session_state["usuario"]
        tipo_cuenta = st.session_state["tipo"]

        st.subheader("🪪 **Información Personal:**")
        st.markdown(f"""
        <div style="border:1px solid #cccccc; border-radius:12px; padding:10px;">
        🏷️ <b>Nombre:</b> {nombre}<br>  
        📧 <b>Email:</b> {email}<br>  
        💎 <b>Tipo de Cuenta:</b> <span style="color:{'gold' if tipo_cuenta == 'Premium' else 'blue'};"><b>{tipo_cuenta}</b></span><br>  
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        st.subheader("📊 **Estado de tu cuenta:**")
        if tipo_cuenta == "Premium":
            st.success("""
            ✔️ Eres usuario **PREMIUM** de Kuyay Skin.  
            ✔️ Tienes acceso ilimitado a:  
            - 🔍 Diagnóstico avanzado.  
            - 🤖 Chat IA Dermatológica.  
            - 🫂 Comunidad y foro privado.  
            - 🎥 Videollamadas con dermatólogo.  
            - 🎁 Descuentos y beneficios exclusivos.  
            ✔️ ¡Gracias por ser parte de la comunidad Premium! 💖
            """)
        else:
            st.info("""
            ➕ Actualmente tienes una cuenta **FREE**.  
            ✅ Acceso básico a:  
            - Diagnóstico de piel básico.  
            - Cuestionario dermatológico.  
            - Rutinas y educación general.  

            🎯 **¡Mejora tu experiencia!**  
            ➝ Actualiza a **Premium** para acceder a beneficios exclusivos como Chat IA, Comunidad, Videollamada y Descuentos.  
            """)

        st.divider()

        st.subheader("⚙️ **Configuraciones rápidas:**")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🔒 Cerrar sesión"):
                st.session_state.clear()
                st.rerun()

        with col2:
            st.button("🗑️ Eliminar datos (Demo)", disabled=True)

        st.caption("⚠️ *Funcionalidad de eliminación de datos no disponible en esta demo.*")

        st.divider()

        st.subheader("📜 **Términos y condiciones:**")
        st.markdown("""
        Al usar Kuyay Skin, aceptas nuestros términos de uso. Esta app es una herramienta de orientación dermatológica y no reemplaza una consulta médica profesional.

        ✔️ Tu información es confidencial y se usa únicamente dentro de esta plataforma.  
        ✔️ Puedes cancelar tu suscripción Premium en cualquier momento desde el centro de ayuda.  
        """)

        st.divider()

        st.markdown("💖 **Gracias por ser parte de Kuyay Skin. Tu piel, tu historia, tu cuidado.**")

