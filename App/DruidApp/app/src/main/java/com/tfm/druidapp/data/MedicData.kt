package com.tfm.druidapp.data

import androidx.compose.material3.MaterialTheme
import androidx.compose.ui.graphics.Color
import com.tfm.druidapp.ui.theme.LightTransparentGrey

////////////////////// MEDIC INFO //////////////////////
data class NormalRange<T : Number>(
    val min: T,
    val max: T
)

data class NormalMedicRanges(
    val ppm: NormalRange<Int> = NormalRange(60,100),
    //val ibi: NormalRange<Float>? = null,
    //val frequency: NormalRange<Float>? = null,
    val sdnn: NormalRange<Float> = NormalRange(50f,150f),
    val rmsdd: NormalRange<Float> = NormalRange(20f,50f),
    //val amplitude: NormalRange<Float>? = null,
    val riseTime: NormalRange<Float> = NormalRange(100f,200f),
    val sys: NormalRange<Int> = NormalRange(108,139),
    val dia: NormalRange<Int> = NormalRange(65,89),
    val temperature: NormalRange<Float> = NormalRange(35f,37.7f)
)

object MedicUtilities{
    fun calculateNormalRanges(age: Int, gender: String): NormalMedicRanges {
        var ranges = NormalMedicRanges()

        //Ritmo cardíaco
        ranges = when{
            age <= 1->{ranges.copy(ppm = NormalRange(70,190))}
            age <= 2->{ranges.copy(ppm = NormalRange(80,130))}
            age <= 4->{ranges.copy(ppm = NormalRange(80,120))}
            age <= 6->{ranges.copy(ppm = NormalRange(75,115))}
            age <= 9->{ranges.copy(ppm = NormalRange(70,110))}
            else->{ranges.copy(ppm = NormalRange(60,100))}
        }

        //Presión arterial
        ranges = when {
            age <= 18 -> {
                if (gender == "Hombre") {
                    ranges.copy(
                        sys = NormalRange(105, 135),
                        dia = NormalRange(60, 86)
                    )
                } else {
                    ranges.copy(
                        sys = NormalRange(100, 130),
                        dia = NormalRange(60, 85)
                    )
                }
            }
            age <= 24 -> {
                if (gender == "Hombre") {
                    ranges.copy(
                        sys = NormalRange(105, 139),
                        dia = NormalRange(62, 88)
                    )
                } else {
                    ranges.copy(
                        sys = NormalRange(100, 130),
                        dia = NormalRange(60, 85)
                    )
                }
            }
            age <= 29 -> {
                if (gender == "Hombre") {
                    ranges.copy(
                        sys = NormalRange(108, 139),
                        dia = NormalRange(65, 89)
                    )
                } else {
                    ranges.copy(
                        sys = NormalRange(102, 135),
                        dia = NormalRange(60, 86)
                    )
                }
            }
            age <= 39 -> {
                if (gender == "Hombre") {
                    ranges.copy(
                        sys = NormalRange(110, 145),
                        dia = NormalRange(68, 92)
                    )
                } else {
                    ranges.copy(
                        sys = NormalRange(105, 139),
                        dia = NormalRange(65, 89)
                    )
                }
            }
            age <= 49 -> {
                if (gender == "Hombre") {
                    ranges.copy(
                        sys = NormalRange(110, 150),
                        dia = NormalRange(70, 96)
                    )
                } else {
                    ranges.copy(
                        sys = NormalRange(105, 150),
                        dia = NormalRange(65, 96)
                    )
                }
            }
            age <= 59 -> {
                if (gender == "Hombre") {
                    ranges.copy(
                        sys = NormalRange(115, 155),
                        dia = NormalRange(70, 98)
                    )
                } else {
                    ranges.copy(
                        sys = NormalRange(110, 155),
                        dia = NormalRange(70, 98)
                    )
                }
            }
            else -> {
                if (gender == "Hombre") {
                    ranges.copy(
                        sys = NormalRange(115, 160),
                        dia = NormalRange(70, 100)
                    )
                } else {
                    ranges.copy(
                        sys = NormalRange(115, 160),
                        dia = NormalRange(70, 100)
                    )
                }
            }
        }

        return ranges
    }

    data class MedicDataColors(
        val onCorrect: Color = Color.White,
        val onIncorrect: Color = Color.Red,
        val onIdle: Color = LightTransparentGrey
    )
    fun setColor(value: Int?, range: NormalRange<Int>, enabled: Boolean, colors: MedicDataColors = MedicDataColors()): Color{
        return if(enabled){
            value?.let {
                if(it in range.min..range.max){
                    colors.onCorrect
                }else{
                    colors.onIncorrect
                }
            } ?: colors.onIdle
        }else{
            colors.onIdle
        }
    }
    fun setColor(value: Float?, range: NormalRange<Float>, enabled: Boolean, colors: MedicDataColors = MedicDataColors()): Color{
        return if(enabled){
            value?.let {
                if(it in range.min..range.max){
                    colors.onCorrect
                }else{
                    colors.onIncorrect
                }
            } ?: colors.onIdle
        }else{
            colors.onIdle
        }
    }
}


////////////////////// GLASGOW //////////////////////
data class GlasgowTestItem(
    val text: String,
    val score: Int
)

sealed class GlasgowData(val options: List<GlasgowTestItem>) {
    data object EyeOpening : GlasgowData(
        listOf(
            GlasgowTestItem("Espontánea", 4),
            GlasgowTestItem("A la orden", 3),
            GlasgowTestItem("Ante estímulo doloroso", 2),
            GlasgowTestItem("Ausencia de apertura ocular", 1)
        )
    )

    data object VerbalResponse : GlasgowData(
        listOf(
            GlasgowTestItem("Orientado correctamente", 5),
            GlasgowTestItem("Paciente confuso", 4),
            GlasgowTestItem("Lenguaje inapropiado", 3),
            GlasgowTestItem("Lenguaje incomprensible", 2),
            GlasgowTestItem("Carencia de actividad verbal", 1)
        )
    )

    data object MotorResponse : GlasgowData(
        listOf(
            GlasgowTestItem("Obedece órdenes correctamente", 6),
            GlasgowTestItem("Localiza estímulos dolorosos", 5),
            GlasgowTestItem("Responde al estímulo doloroso pero no localiza", 4),
            GlasgowTestItem("Respuesta con flexión anormal de los miembros", 3),
            GlasgowTestItem("Respuesta con extensión anormal de los miembros", 2),
            GlasgowTestItem("Ausencia de respuesta motora", 1)
        )
    )
}