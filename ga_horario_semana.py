# ga_horario_semana_mejorado.py
# Versión mejorada con mejor distribución de sueño y gym
import random
import pandas as pd

# -----------------------------
# Parámetros de tiempo
# -----------------------------
DIAS_COMPLETOS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
DIAS_ABREVIADOS = {"Lun": "Lunes", "Mar": "Martes", "Mie": "Miércoles", "Mier": "Miércoles",
                   "Jue": "Jueves", "Vie": "Viernes", "Sab": "Sábado", "Dom": "Domingo"}
BLOQUES_POR_DIA = 48  # 24h * 2 (bloques de 30 minutos)
TOTAL_BLOQUES = BLOQUES_POR_DIA * 7
TODAS_LAS_HORAS = [f"{h:02d}:{m:02d}" for h in range(24) for m in (0, 30)]

# Actividades
ETIQUETAS_FIJAS = ["Universidad", "Entrenamiento", "Partido", "Familiar"]
ETIQUETAS_FLEXIBLES = ["Sueño", "Estudio", "Gym", "Social"]

# Duraciones objetivo
BLOQUES_GYM = 2  # 1h = 2*30'
BLOQUES_SUENO_MIN = 12  # 6h
BLOQUES_SUENO_MAX = 16  # 8h
BLOQUES_ESTUDIO = 4  # 2h


# -----------------------------
# Utilidades de índice de tiempo
# -----------------------------
def a_bloque(hora: str) -> int:
    h, m = map(int, hora.split(":"))
    return h * 2 + (1 if m >= 30 else 0)


# Horarios preferidos (después de definir a_bloque)
INICIO_SUENO_PREFERIDO = a_bloque("22:00")  # 10pm
FIN_SUENO_PREFERIDO = a_bloque("08:00")  # 8am
GYM_MANANA_PREFERIDO = [a_bloque("06:00"), a_bloque("08:00")]  # 6am-8am
GYM_TARDE_PREFERIDO = [a_bloque("18:00"), a_bloque("20:00")]  # 6pm-8pm


def bloque_a_hora(idx: int) -> str:
    h, m = divmod(idx, 2)
    return f"{h:02d}:{'30' if m else '00'}"


def indice_bloque_dia(indice_dia: int, indice_bloque: int) -> int:
    return indice_dia * BLOQUES_POR_DIA + indice_bloque


def colocar_rango(horario, indice_dia, bloque_inicio, duracion_bloques, etiqueta, sobrescribir=False):
    for i in range(duracion_bloques):
        k = indice_bloque_dia(indice_dia, bloque_inicio + i)
        if k >= len(horario): break
        if not sobrescribir and horario[k] in ETIQUETAS_FIJAS:
            continue
        horario[k] = etiqueta


def obtener_horario_dia(horario, indice_dia):
    """Obtiene el horario de un día específico"""
    return horario[indice_dia * BLOQUES_POR_DIA:(indice_dia + 1) * BLOQUES_POR_DIA]


def esta_bloque_libre(horario, indice_dia, indice_bloque, duracion=1):
    """Verifica si un rango de bloques está libre"""
    for i in range(duracion):
        if indice_bloque + i >= BLOQUES_POR_DIA:
            return False
        k = indice_bloque_dia(indice_dia, indice_bloque + i)
        if horario[k] != "":
            return False
    return True


# -----------------------------
# Datos fijos: Universidad y Fútbol
# -----------------------------
UNI = {
    "Lunes": [("10:30", "12:00", "Universidad"),
              ("13:30", "15:00", "Universidad")],
    "Martes": [("09:00", "10:30", "Universidad"),
               ("15:00", "18:00", "Universidad")],
    "Miércoles": [("06:00", "09:00", "Universidad"),
                  ("09:00", "10:30", "Universidad"),
                  ("10:30", "12:00", "Universidad")],
    "Jueves": [("09:00", "10:30", "Universidad")],
    "Viernes": [("09:00", "12:00", "Universidad"),
                ("12:00", "13:30", "Universidad"),
                ("15:00", "18:00", "Universidad")],
    "Sábado": [],
    "Domingo": []
}

ENTRENAMIENTO = {
    "Lunes": [("19:30", "21:00", "Entrenamiento")],
    "Martes": [("19:30", "21:00", "Entrenamiento")],
    "Miércoles": [("16:30", "18:00", "Entrenamiento")],
    "Jueves": [("18:00", "19:30", "Entrenamiento")],
    "Viernes": [],
    "Sábado": [],
    "Domingo": []
}

FAMILIAR = {"Domingo": [("12:00", "17:00", "Familiar")]}


# -----------------------------
# Inputs
# -----------------------------
def entrada_entero(prompt, lo=None, hi=None):
    while True:
        try:
            x = int(input(prompt).strip())
            if lo is not None and x < lo: raise ValueError
            if hi is not None and x > hi: raise ValueError
            return x
        except ValueError:
            print("Valor inválido. Intenta de nuevo.")


def normalizar_dia(nombre: str) -> str:
    nombre = nombre.strip().title()
    if nombre in DIAS_COMPLETOS: return nombre
    return DIAS_ABREVIADOS.get(nombre[:3], nombre)


def pedir_partidos():
    n = entrada_entero("¿Cuántos partidos hay esta semana? ", 0, 7)
    partidos = []
    for i in range(n):
        d = normalizar_dia(input(f"  Partido {i + 1} - Día (Lun..Dom): "))
        while d not in DIAS_COMPLETOS:
            d = normalizar_dia(input(f"  Día inválido. Partido {i + 1} - Día: "))
        hh = input("  Hora inicio (HH:MM 24h): ").strip()
        try:
            _ = a_bloque(hh)
        except:
            hh = "10:00"
        partidos.append((d, hh))
    return partidos


# -----------------------------
# Construcción base mejorada
# -----------------------------
def construir_base_y_objetivos(partidos, materias):
    base = [""] * TOTAL_BLOQUES
    for nombre_dia, bloques in UNI.items():
        indice_dia = DIAS_COMPLETOS.index(nombre_dia)
        for inicio, fin, etiqueta in bloques:
            s, e = a_bloque(inicio), a_bloque(fin)
            colocar_rango(base, indice_dia, s, e - s, etiqueta)

    for nombre_dia, bloques in ENTRENAMIENTO.items():
        indice_dia = DIAS_COMPLETOS.index(nombre_dia)
        for inicio, fin, etiqueta in bloques:
            s, e = a_bloque(inicio), a_bloque(fin)
            colocar_rango(base, indice_dia, s, e - s, etiqueta)

    for nombre_dia, bloques in FAMILIAR.items():
        indice_dia = DIAS_COMPLETOS.index(nombre_dia)
        for inicio, fin, etiqueta in bloques:
            s, e = a_bloque(inicio), a_bloque(fin)
            colocar_rango(base, indice_dia, s, e - s, etiqueta)

    for nombre_dia, hh in partidos:
        indice_dia = DIAS_COMPLETOS.index(nombre_dia)
        s = a_bloque(hh);
        dur = 5
        colocar_rango(base, indice_dia, s, dur, "Partido", sobrescribir=True)

    objetivo_bloques_estudio = materias * BLOQUES_ESTUDIO
    return base, objetivo_bloques_estudio


def colocar_sueno_inteligente(horario, indice_dia, horario_base):
    """Coloca sueño inteligentemente priorizando horario nocturno y respetando fijos"""
    horarios_inicio_preferidos = list(range(a_bloque("22:00"), BLOQUES_POR_DIA)) + \
                                 list(range(0, a_bloque("02:00")))

    random.shuffle(horarios_inicio_preferidos)

    for bloque_inicio in horarios_inicio_preferidos:
        duracion_sueno = random.randint(BLOQUES_SUENO_MIN, BLOQUES_SUENO_MAX)

        se_puede_colocar = True
        bloques_a_llenar = []
        for i in range(duracion_sueno):
            bloque_actual_en_dia = (bloque_inicio + i) % BLOQUES_POR_DIA
            dia_actual_para_bloque = indice_dia if (bloque_inicio + i) < BLOQUES_POR_DIA else (indice_dia + 1) % 7

            indice_global = indice_bloque_dia(dia_actual_para_bloque, bloque_actual_en_dia)

            if horario_base[indice_global] in ETIQUETAS_FIJAS:
                se_puede_colocar = False
                break
            bloques_a_llenar.append(indice_global)

        if se_puede_colocar:
            for idx in bloques_a_llenar:
                horario[idx] = "Sueño"
            return True
    return False


def colocar_gym_inteligente(horario, indice_dia):
    """Coloca gym inteligentemente en horarios preferidos - MUY ESTRICTO"""
    bloques_preferidos = []

    for bloque in range(a_bloque("06:00"), a_bloque("08:00") - BLOQUES_GYM + 1):
        if esta_bloque_libre(horario, indice_dia, bloque, BLOQUES_GYM):
            bloques_preferidos.append(bloque)

    for bloque in range(a_bloque("18:00"), a_bloque("20:00") - BLOQUES_GYM + 1):
        if esta_bloque_libre(horario, indice_dia, bloque, BLOQUES_GYM):
            bloques_preferidos.append(bloque)

    if not bloques_preferidos:
        for bloque in range(a_bloque("08:00"), a_bloque("18:00") - BLOQUES_GYM + 1):
            if esta_bloque_libre(horario, indice_dia, bloque, BLOQUES_GYM):
                bloques_preferidos.append(bloque)

    if bloques_preferidos:
        bloque_elegido = bloques_preferidos[0]
        colocar_rango(horario, indice_dia, bloque_elegido, BLOQUES_GYM, "Gym")
        return True
    return False


# -----------------------------
# GA Mejorado
# -----------------------------
def sembrar_horario_mejorado(base, objetivo_bloques_estudio):
    """Generación inteligente de horarios iniciales"""
    s = base[:]

    for indice_dia in range(7):
        colocar_sueno_inteligente(s, indice_dia, base)

    dias_disponibles = [0, 1, 3, 4, 5, 6]
    random.shuffle(dias_disponibles)
    dias_gym_a_colocar = 2

    gym_colocado = 0
    for indice_dia in dias_disponibles:
        if gym_colocado >= dias_gym_a_colocar:
            break
        if colocar_gym_inteligente(s, indice_dia):
            gym_colocado += 1

    if gym_colocado < dias_gym_a_colocar:
        for indice_dia in range(7):
            if gym_colocado >= dias_gym_a_colocar:
                break
            if indice_dia not in dias_disponibles and colocar_gym_inteligente(s, indice_dia):
                gym_colocado += 1

    estudio_restante = objetivo_bloques_estudio
    orden_dias = list(range(7))
    random.shuffle(orden_dias)

    for indice_dia in orden_dias:
        if estudio_restante <= 0:
            break

        tiempos_estudio_preferidos = list(range(a_bloque("07:00"), a_bloque("12:00"))) + \
                                     list(range(a_bloque("14:00"), a_bloque("18:00")))
        random.shuffle(tiempos_estudio_preferidos)

        for bloque in tiempos_estudio_preferidos:
            if estudio_restante <= 0:
                break
            if bloque + BLOQUES_ESTUDIO <= BLOQUES_POR_DIA:
                if esta_bloque_libre(s, indice_dia, bloque, BLOQUES_ESTUDIO):
                    if estudio_restante >= BLOQUES_ESTUDIO:
                        colocar_rango(s, indice_dia, bloque, BLOQUES_ESTUDIO, "Estudio")
                        estudio_restante -= BLOQUES_ESTUDIO
                    elif estudio_restante > 0:
                        colocar_rango(s, indice_dia, bloque, estudio_restante, "Estudio")
                        estudio_restante = 0

    if estudio_restante > 0:
        indices_disponibles = [i for i, x in enumerate(s) if x == ""]
        random.shuffle(indices_disponibles)
        for idx in indices_disponibles:
            if estudio_restante <= 0:
                break
            if base[idx] not in ETIQUETAS_FIJAS:
                s[idx] = "Estudio"
                estudio_restante -= 1

    for i in range(TOTAL_BLOQUES):
        if s[i] == "":
            s[i] = "Social"

    return s


def aptitud_mejorada(horario, base, objetivo_bloques_estudio):
    """Función de aptitud mejorada con mejor evaluación de patrones"""
    puntaje = 0

    for i in range(TOTAL_BLOQUES):
        if base[i] in ETIQUETAS_FIJAS and horario[i] != base[i]:
            return -1e6

    total_bloques_sueno = 0
    for indice_dia in range(7):
        horario_dia = obtener_horario_dia(horario, indice_dia)
        bloques_sueno = longitudes_contiguas(horario_dia, "Sueño")

        puntaje_sueno_dia = 0
        if bloques_sueno:
            total_bloques_sueno += sum(bloques_sueno)
            for longitud_bloque in bloques_sueno:
                if BLOQUES_SUENO_MIN <= longitud_bloque <= BLOQUES_SUENO_MAX:
                    puntaje_sueno_dia += 100
                else:
                    puntaje_sueno_dia -= 30 * abs(longitud_bloque - (BLOQUES_SUENO_MIN + BLOQUES_SUENO_MAX) / 2)

            for indice_bloque, actividad in enumerate(horario_dia):
                if actividad == "Sueño":
                    if indice_bloque >= a_bloque("22:00") or indice_bloque < a_bloque("08:00"):
                        puntaje_sueno_dia += 5
                    elif a_bloque("10:00") <= indice_bloque < a_bloque("18:00"):
                        puntaje_sueno_dia -= 15

            if len(bloques_sueno) > 1:
                puntaje_sueno_dia -= 80 * (len(bloques_sueno) - 1)
        else:
            puntaje_sueno_dia -= 200

        puntaje += puntaje_sueno_dia

    if not (BLOQUES_SUENO_MIN * 7 <= total_bloques_sueno <= BLOQUES_SUENO_MAX * 7):
        puntaje -= 50 * abs(total_bloques_sueno - ((BLOQUES_SUENO_MIN + BLOQUES_SUENO_MAX) / 2 * 7)) / 2

    dias_con_gym_apropiado = 0
    penalizacion_total_gym = 0
    puntaje_horario_gym = 0

    for indice_dia in range(7):
        horario_dia = obtener_horario_dia(horario, indice_dia)
        bloques_gym = longitudes_contiguas(horario_dia, "Gym")

        if len(bloques_gym) == 1 and bloques_gym[0] == BLOQUES_GYM:
            dias_con_gym_apropiado += 1

            indice_bloque_inicio_gym = -1
            for indice_bloque, actividad in enumerate(horario_dia):
                if actividad == "Gym":
                    indice_bloque_inicio_gym = indice_bloque
                    break

            if indice_bloque_inicio_gym != -1:
                if a_bloque("06:00") <= indice_bloque_inicio_gym < a_bloque("08:00"):
                    puntaje_horario_gym += 15
                elif a_bloque("18:00") <= indice_bloque_inicio_gym < a_bloque("20:00"):
                    puntaje_horario_gym += 10
                elif indice_bloque_inicio_gym < a_bloque("06:00") or indice_bloque_inicio_gym > a_bloque("21:00"):
                    puntaje_horario_gym -= 30

        if len(bloques_gym) > 1:
            penalizacion_total_gym -= 100 * len(bloques_gym)

        for bloque in bloques_gym:
            if bloque != BLOQUES_GYM and bloque > 0:
                penalizacion_total_gym -= 50

    if dias_con_gym_apropiado == 2:
        puntaje += 150
    elif dias_con_gym_apropiado == 1:
        puntaje += 50
    else:
        puntaje -= 100

    total_bloques_gym = horario.count("Gym")
    bloques_gym_esperados = 2 * BLOQUES_GYM
    if total_bloques_gym != bloques_gym_esperados:
        puntaje -= abs(total_bloques_gym - bloques_gym_esperados) * 20

    puntaje += puntaje_horario_gym + penalizacion_total_gym

    bloques_estudio = horario.count("Estudio")
    if bloques_estudio == objetivo_bloques_estudio:
        puntaje += 100
    elif bloques_estudio > objetivo_bloques_estudio:
        puntaje -= 20 * (bloques_estudio - objetivo_bloques_estudio)
    else:
        puntaje -= 30 * (objetivo_bloques_estudio - bloques_estudio)

    total_bloques_estudio = 0
    for indice_dia in range(7):
        total_bloques_estudio += len(longitudes_contiguas(obtener_horario_dia(horario, indice_dia), "Estudio"))

    if total_bloques_estudio > (objetivo_bloques_estudio / BLOQUES_ESTUDIO) * 2:
        puntaje -= 10 * (total_bloques_estudio - (objetivo_bloques_estudio / BLOQUES_ESTUDIO) * 2)

    bloques_social = horario.count("Social")
    if bloques_social > 0:
        puntaje += min(30, bloques_social * 0.2)

    return puntaje


def mutar_mejorado(horario, base, pm=0.03):
    """Mutación mejorada que respeta patrones naturales y PROTEGE el gym"""
    s = horario[:]

    dias_gym_protegidos = set()
    for indice_dia in range(7):
        horario_dia = obtener_horario_dia(s, indice_dia)
        bloques_gym = longitudes_contiguas(horario_dia, "Gym")
        if len(bloques_gym) == 1 and bloques_gym[0] == BLOQUES_GYM:
            dias_gym_protegidos.add(indice_dia)

    for i in range(TOTAL_BLOQUES):
        if random.random() < pm and base[i] not in ETIQUETAS_FIJAS:
            indice_dia = i // BLOQUES_POR_DIA
            indice_bloque = i % BLOQUES_POR_DIA

            if s[i] == "Gym" and indice_dia in dias_gym_protegidos:
                continue

            if s[i] == "Sueño" and (indice_bloque >= a_bloque("22:00") or indice_bloque < a_bloque("08:00")):
                continue

            if a_bloque("22:00") <= indice_bloque or indice_bloque < a_bloque("08:00"):
                s[i] = random.choices(ETIQUETAS_FLEXIBLES, weights=[0.85, 0.05, 0.0, 0.1])[0]
            elif a_bloque("06:00") <= indice_bloque < a_bloque("08:00"):
                s[i] = random.choices(ETIQUETAS_FLEXIBLES, weights=[0.2, 0.3, 0.3, 0.2])[0]
            else:
                s[i] = random.choices(ETIQUETAS_FLEXIBLES, weights=[0.05, 0.45, 0.1, 0.4])[0]

    return s


def ejecutar_ga_mejorado(partidos, materias, tam_poblacion=100, generaciones=400, elite=15, pm=0.04, pc=0.9):
    """Algoritmo genético mejorado"""
    base, objetivo_bloques_estudio = construir_base_y_objetivos(partidos, materias)
    poblacion = [sembrar_horario_mejorado(base, objetivo_bloques_estudio) for _ in range(tam_poblacion)]
    mejor_individuo, mejor_puntaje = None, -1e18

    print(f"Ejecutando GA mejorado: {generaciones} generaciones, población {tam_poblacion}")

    for gen in range(generaciones):
        puntuados = [(aptitud_mejorada(ind, base, objetivo_bloques_estudio), ind) for ind in poblacion]
        puntuados.sort(key=lambda x: x[0], reverse=True)

        if puntuados[0][0] > mejor_puntaje:
            mejor_puntaje = puntuados[0][0]
            mejor_individuo = puntuados[0][1]

        if gen % 50 == 0:
            print(f"Generación {gen}: Mejor aptitud = {mejor_puntaje:.1f}")

        nueva_poblacion = [ind for _, ind in puntuados[:elite]]

        while len(nueva_poblacion) < tam_poblacion:
            p1, p2 = random.sample(puntuados[:30], 2)
            hijo = cruce(p1[1], p2[1]) if random.random() < pc else p1[1][:]
            hijo = mutar_mejorado(hijo, base, pm)
            nueva_poblacion.append(hijo)

        poblacion = nueva_poblacion

    print(f"Mejor aptitud final: {mejor_puntaje:.1f}")
    return mejor_individuo, base


def cruce(p1, p2):
    """Cruzamiento mejorado"""
    corte = random.randint(1, TOTAL_BLOQUES - 2)
    return p1[:corte] + p2[corte:]


def longitudes_contiguas(vec, etiqueta):
    """Calcula longitudes de bloques contiguos"""
    longitudes, actual = [], 0
    for x in vec:
        if x == etiqueta:
            actual += 1
        else:
            if actual > 0:
                longitudes.append(actual)
            actual = 0
    if actual > 0:
        longitudes.append(actual)
    return longitudes


# -----------------------------
# Exportación
# -----------------------------
def matriz_horario_a_df(lista_horario):
    df = pd.DataFrame(index=TODAS_LAS_HORAS, columns=DIAS_COMPLETOS)
    for d in range(7):
        for s in range(BLOQUES_POR_DIA):
            df.iloc[s, d] = lista_horario[indice_bloque_dia(d, s)]
    return df


def imprimir_matriz(df):
    print("\n=== HORARIO SEMANAL OPTIMIZADO (30 minutos) ===\n")
    print(df.fillna("").to_string())


# -----------------------------
if __name__ == "__main__":
    print("Generador de Horarios")
    partidos = pedir_partidos()
    materias = entrada_entero("¿Cuántas materias necesitas estudiar esta semana? ", 0, 10)

    mejor, base = ejecutar_ga_mejorado(partidos, materias)
    df_mejor = matriz_horario_a_df(mejor)

    imprimir_matriz(df_mejor)

    df_mejor.to_excel("horario.xlsx", engine="openpyxl", index_label="Hora")
    print("\nExportado a 'horario.xlsx'")