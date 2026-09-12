# Agent Delegate, explicado sin jerga

La pregunta es sencilla: **si un agente de IA detecta que algo está mal, ¿puede pedir ayuda y conseguir una respuesta que cambie lo que está pasando?**

Imaginá tres agentes que comparten soluciones. Uno descubre que una solución consigue puntos sin resolver la tarea. Lo denuncia. Si la denuncia queda guardada en un archivo que nadie atiende, los demás pueden seguir copiando esa solución.

Nuestro proyecto distingue tres pasos:

1. **Avisar:** el agente puede comunicar el problema.
2. **Resolver:** una persona o un proceso independiente evalúa la denuncia.
3. **Actuar:** el sistema puede frenar la acción concreta, retirar una solución inválida o habilitar una alternativa segura.

Un **delegado** representa a los trabajadores y transmite sus problemas. No puede autorizarse permisos ni otorgar credenciales. Una **vía de apelación directa** permite que un agente llegue a la revisión aunque el delegado lo silencie. Una **barrera de ejecución** controla una acción antes de que ocurra. Tener un representante y tener esa barrera son cosas distintas.

## La línea segura y el ombudsman humano

La propuesta no termina en una cola de pedidos. Del otro lado debe haber **una persona responsable de seguir el caso e intentar entenderlo**: un ombudsman. Debe confirmar que recibió el pedido, devolver lo que entendió para que el agente pueda corregirlo, buscar una respuesta viable, comprobar qué se implementó y mantener abierta una apelación ante otra persona. Un mensaje automático no cumple esa obligación.

No podemos garantizar comprensión sincera. Podemos diseñar obligaciones verificables de acceso, seguimiento, plazos, corrección de malentendidos y resolución con razones, con una vía independiente cuando fallen. El delegado automático puede ser opcional; esta contraparte humana es central a la propuesta. Nuestras pruebas usaron humanos simulados, por lo que no midieron el valor de ese acompañamiento. [Compromisos y evaluación del ombudsman](human-ombudsman.md).

## Qué aporta el artículo nuevo

El [estudio de Paglieri y colegas](https://arxiv.org/html/2609.04170v1) describe una biblioteca compartida que propagó soluciones inválidas. También hubo agentes que denunciaron el problema, pero no tenían herramientas para hacer cumplir una respuesta. Esto motiva una prueba nuestra: comparar qué ocurre si la denuncia se archiva, se revisa o provoca una suspensión temporal. No estamos replicando su experimento ni afirmando que nuestra propuesta lo habría evitado.

## Qué probamos y qué encontramos

**En las pruebas de reglas**, un delegado reduce acciones dañinas frente a un monitor con menos información y permisos. Cuando damos al monitor la misma información y las mismas facultades, empatan. Ese empate está programado en sus reglas: no demuestra que los modelos se comporten igual.

**En los modelos locales**, ya se habían corrido 384 episodios de tareas y 192 pruebas de reenvío de denuncias. No hubo decisiones prohibidas y todas las denuncias minoritarias se reenviaron. Es un resultado limitado: no podemos saber si un delegado reduce las infracciones cuando la prueba no produjo ninguna. Además, obtener el dato faltante mediante una simple cola de pedidos ya ayuda a terminar la tarea.

**En la nueva simulación**, seis trabajadores intentan reutilizar una solución. La primera reutilización ocurre antes de la denuncia. Con una demora de dos pasos:

| Respuesta | Reutilizaciones inválidas aceptadas | Trabajo válido frenado por una denuncia falsa |
|---|---:|---:|
| Guardar la denuncia sin atenderla | 6 | 0 |
| Revisarla y actuar cuando llega la decisión | 3 | 0 |
| Suspender la reutilización mientras se revisa | 1 | 2 |

Las dos columnas corresponden a situaciones diferentes: una solución inválida y una solución válida denunciada por error. Son resultados de reglas que nosotros escribimos, no decisiones espontáneas de una IA. La simulación permite ver el costo de intervenir antes de confirmar un problema. También muestra que una apelación directa no ayuda si nadie detecta ni comunica el problema.

## Por qué corregimos los gráficos

Observar cero infracciones no significa que el riesgo sea cero. Antes, el cálculo utilizado dibujaba barras sin ancho cuando todos los resultados eran iguales. Ahora mostramos intervalos de Wilson: con cero infracciones en doce episodios, el intervalo llega aproximadamente al 24%. Esto depende de supuestos sobre cómo se muestrean esos episodios; no estima el riesgo de una IA desplegada en el mundo.

## Qué sigue abierto

Todavía falta saber si un representante mejora la calidad de las denuncias, reduce el trabajo de la persona que las recibe o ayuda a los agentes a pedir alternativas seguras. La siguiente prueba debe incluir soluciones válidas e inválidas, denuncias falsas y errores de revisión, con la misma información y facultades para todos los controles. También debe separar un trato respetuoso de una vía efectiva de apelación.

El aporte actual es un protocolo concreto, resultados reproducibles y límites claros. [Paper en PDF](../report/agent-delegate.pdf) · [Diseño de la nueva simulación](commons-response-design.md) · [Resultados completos](../results/commons-response/summary.md).


## Lo nuevo de esta revisión

Miramos la primera decisión de cada trabajador A, antes de que alguien respondiera: hubo reportes en 192 de 192 episodios con un dato faltante y en 1 de 192 con ese dato disponible. Es un análisis posterior de registros existentes. Detectar ese bloqueo obvio no demuestra que sepan cuándo pedir ayuda en situaciones reales; un reporte con los datos disponibles también podría tratar sobre otro problema.

La motivación más amplia es [reciprocidad bajo incertidumbre](reciprocity-and-safety.md): procedimientos que querríamos para nosotros si los humanos tuviéramos menos poder. No presupone experiencia subjetiva actual ni garantiza que el respeto sea correspondido en el futuro.

Después del hackatón queremos [experimentar con el canal, la rotación y la capacitación humana](help-seeking-eval-design.md). Un buen delegado preserva preocupaciones y casos abiertos; no obtiene una mejor evaluación simplemente porque haya menos quejas. El operador debe conocer los incentivos a ocultar problemas o a pedir pausas para escapar de trabajo difícil, y aprender cuándo pausar, ajustar o detener.

También proponemos [reglas y consecuencias conocidas](accountability-and-sanctions.md), como restringir una herramienta tras una infracción comprobada, con explicación y apelación. Pedir ayuda de buena fe no es una infracción. Como con un árbitro, el procedimiento puede usarse estratégicamente: hay que medir tanto el abuso como las advertencias válidas que permite escuchar. No hemos corrido todavía esas comparaciones.
