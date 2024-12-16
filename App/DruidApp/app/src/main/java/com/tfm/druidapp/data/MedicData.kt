package com.tfm.druidapp.data

////////////////////// MEDIC INFO //////////////////////


////////////////////// GLASGOW //////////////////////
data class GlasgowTestItem(
    val text: String,
    val score: Int
)

sealed class GlasgowData(val options: List<GlasgowTestItem>){
    data object EyeOpening:GlasgowData(
        listOf(
            GlasgowTestItem("Espontánea",4),
            GlasgowTestItem("A la orden",3),
            GlasgowTestItem("Ante estímulo doloroso",2),
            GlasgowTestItem("Ausencia de apertura ocular",1)
        )
    )
    data object VerbalResponse:GlasgowData(
        listOf(
            GlasgowTestItem("Orientado correctamente",5),
            GlasgowTestItem("Paciente confuso",4),
            GlasgowTestItem("Lenguaje inapropiado",3),
            GlasgowTestItem("Lenguaje incomprensible",2),
            GlasgowTestItem("Carencia de actividad verbal",1)
        )
    )
    data object MotorResponse:GlasgowData(
        listOf(
            GlasgowTestItem("Obedece órdenes correctamente",6),
            GlasgowTestItem("Localiza estímulos dolorosos",5),
            GlasgowTestItem("Responde al estímulo doloroso pero no localiza",4),
            GlasgowTestItem("Respuesta con flexión anormal de los miembros",3),
            GlasgowTestItem("Respuesta con extensión anormal de los miembros",2),
            GlasgowTestItem("Ausencia de respuesta motora",1)
        )
    )
}