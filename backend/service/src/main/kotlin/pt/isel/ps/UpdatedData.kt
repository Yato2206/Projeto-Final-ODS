package org.example

import java.time.Instant

sealed interface UpdatedData {
    data class Message(
        val id: Long,
        val data: Any,
        val action: ActionKind,
    ) : UpdatedData

    data class KeepAlive(
        val timestamp: Instant,
    ) : UpdatedData {
        companion object {
            var count = 1
        }

        val count: Int = Companion.count++

        override fun toString() = "${timestamp.epochSecond} - $count"
    }
}


//preencher com acoes que tenham senso
enum class ActionKind {

}
