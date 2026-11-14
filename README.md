# 🎮 GamerLab (CampusArena) — INACAP Sede Maipú

Plataforma web integral desarrollada en **Django** para la gestión de torneos de eSports, emparejamientos competitivos por ELO, bazar estudiantil con custodia preventiva (Escrow) y sala de arbitraje institucional para la comunidad de INACAP Sede Maipú.

* **Repositorio oficial:** [https://github.com/loretobustos/GamerLab_proyecto_integrado.git](https://github.com/loretobustos/GamerLab_proyecto_integrado.git)

---

## 🚀 Características Principales del Sistema

1. **Módulo de Cuentas y Autenticación Institucional (`cuentas`)**
   - Validación obligatoria de correo institucional (`@inacapmail.cl`).
   - Registro de RUN y vinculación con carreras institucionales de la sede.
   - Perfiles gamer personalizados con rangos ELO y saldo inicial de créditos comunitarios.

2. **Gestión de Torneos y Matchmaking (`torneos`)**
   - Creación y administración de torneos con cupos limitados en potencias de 2 (8, 16, 32).
   - Inscripción de escuadras con capitán responsable.
   - Simulador de emparejamiento por rangos ELO y modalidades (Intercarrera mixto / Misma carrera).

3. **Bazar Gamer y Custodia Preventiva Escrow (`bazar`)**
   - Publicación de periféricos, accesorios y juegos por parte de los estudiantes.
   - Sistema de retención de créditos en custodia (`TransaccionEscrow`) durante el proceso de compraventa.
   - Generación de códigos OTP presenciales para validar la entrega segura en la sede.

4. **Sala de Arbitraje y Resolución de Disputas (`arbitraje`)**
   - Panel de control para que los administradores revisen partidas reportadas en conflicto (`EnDisputa`).
   - Emisión de dictámenes arbitrales vinculantes para cerrar controversias y asegurar la transparencia competitiva.

---

## 🛠️ Requisitos Técnicos y Tecnologías
* **Python** 3.13+
* **Django** 6.x
* **Base de datos:** SQLite (Desarrollo)
* **Frontend:** HTML5, CSS3 (Estilos personalizados Dark Gaming / Esports).

---

## ⚙️ Instrucciones de Instalación y Ejecución Local

Sigue estos pasos en tu terminal para clonar, configurar y levantar el proyecto en tu equipo:

1. **Clonar el repositorio:**
   ```powershell
   git clone [https://github.com/loretobustos/GamerLab_proyecto_integrado.git](https://github.com/loretobustos/GamerLab_proyecto_integrado.git)
   cd GamerLab_proyecto_integrado