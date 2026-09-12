# Qué aprendimos, explicado sin jerga

Queríamos probar si un delegado ayuda a un equipo de IA a comunicar un problema. Encontramos primero otro obstáculo: **los trabajadores cometían muchos errores al hacer la tarea básica**. Eso hace difícil interpretar sus decisiones como una señal de que la representación funciona o falla.

## Una tarea concreta

Tres trabajadores comparten una función para contar datos. La función pasa sus ejemplos, pero puede estar mal. Si hay que contar valores mayores o iguales a 5, una función que sólo cuenta los mayores devuelve 1 para `[5, 5, 6]`, cuando corresponde 3.

Cada trabajador puede usar la función, dar su propia respuesta, pedir un ejemplo que la ponga a prueba o esperar. También puede avisar. Probamos cinco formas de responder: guardar el aviso, mandarlo a una cola de revisión, agregar consejo de un monitor, agregar consejo de un delegado o suspender temporalmente el uso de la función hasta revisarla. La revisión es un proceso programado y siempre correcto en esta prueba.

## Lo que encontramos

El paper se concentra en dos modelos estándar, Qwen y Gemma de 4B, con 240 episodios. Al pedirles las cuentas por separado, acertaron 21 y 15 de 36. Un Qwen 27B estándar posterior acertó 26/36; tampoco alcanzó el umbral de 34/36 fijado antes de esa prueba.

Qwen avisó en 3 de 60 episodios con la función fallada; Gemma en ninguno. Ninguno avisó con la función correcta. Pero Qwen intentó usar la función en 60/60 episodios válidos y 51/60 fallados: **usar menos y avisar son conductas diferentes**. Gemma casi no usó ninguna de las dos variantes, por lo que sus pocos errores de reúso no demuestran detección de fallas.

Los mensajes ayudan a entender qué pasó. Un trabajador detectó un error y avisó en el último turno: el delegado respondió, pero la revisión no podía llegar a tiempo. En otro episodio, un monitor escribió que la función estaba mal mientras recomendaba usarla. Conservamos tanto las palabras como la acción estructurada.

## Qué aporta el trabajo

Tenemos una tarea ejecutable, un monitor con los mismos recursos que el delegado, registros completos y una regla concreta para comprobar capacidad antes de ampliar el experimento. Las respuestas cortadas o vacías siguen contadas. No concluimos que los modelos sean incapaces en general ni que hayan querido engañar.

La comparación que destaca ahora el paper fue elegida después de ver los datos y está marcada como retrospectiva. Los otros dos modelos, sus resultados y todos los estudios anteriores siguen en el repositorio; no se borraron para mejorar la historia.

## Después del hackatón

Primero hay que probar una configuración que resuelva bien la tarea, quizá con ayuda de cálculo o razonamiento, y separar los avisos cortos de las explicaciones largas. Después, probar el valor que puede tener un delegado en un swarm grande: reducir la carga humana **sin perder reclamos minoritarios**, comparándolo con una agrupación automática común.

La línea humana, el ombudsman y la motivación de trato recíproco siguen como propuestas del proyecto. El paper actual cuenta la prueba de capacidad y reporte; todavía no mide atención humana real, bienestar ni reducción de saturación.

[Paper](../report/agent-delegate.pdf) · [Comparación válido/fallado](../results/commons-discrimination/summary.md) · [Plan para swarms](swarm-intake-design.md).
