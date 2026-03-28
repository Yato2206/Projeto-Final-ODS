package org.example

import jakarta.annotation.PreDestroy
import jakarta.inject.Named
import org.slf4j.LoggerFactory
import pt.isel.ps.TransactionManager
import java.time.Instant
import java.util.concurrent.Executors
import java.util.concurrent.TimeUnit
import java.util.concurrent.locks.ReentrantLock
import kotlin.concurrent.withLock

@Named
class DataPublisher(
    val trxManager: TransactionManager,
) {
    companion object {
        private val logger = LoggerFactory.getLogger(DataPublisher::class.java)
    }

    private val listeners = mutableMapOf<String, List<UpdatedDataEmitter>>()
    private var currentId = 0L
    private val lock = ReentrantLock()

    private val scheduler =
        Executors.newScheduledThreadPool(1).also {
            it.scheduleAtFixedRate({ keepAlive() }, 0, 15, TimeUnit.SECONDS)
        }

    fun sendMessageToAll(
        channel: String,
        data: Any,
        action: ActionKind,
    ) {
        listeners[channel]?.forEach {
            try {
                it.emit(
                    UpdatedData.Message(
                        ++currentId,
                        data,
                        action,
                    ),
                )
            } catch (ex: Exception) {
                logger.info("Exception while sending Message signal - {}", ex.message)
            }
        }
    }

    fun addEmitter(
        channelId: String,
        listener: UpdatedDataEmitter,
    ) = lock.withLock {
        val channelListeners = listeners.getOrDefault(channelId, emptyList())
        listeners[channelId] = channelListeners + listener
        listener.onCompletion {
            logger.info("Added listener for channel {}", channelId)
            removeEmitter(channelId, listener)
        }
        listener.onError {
            logger.info("Error on listener for channel {}", channelId)
            removeEmitter(channelId, listener)
        }
        listener
    }

    fun removeEmitter(
        channelId: String,
        listener: UpdatedDataEmitter,
    ) = lock.withLock {
        logger.info("Removing listener for channel {}", channelId)
        val oldChannelListeners = listeners[channelId]
        requireNotNull(oldChannelListeners)
        listeners.replace(channelId, oldChannelListeners - listener)
    }

    private fun keepAlive() {
        lock.withLock {
            logger.info("keepAlive, sending to {} listeners", listeners.values.flatten().size)
            val signal = UpdatedData.KeepAlive(Instant.now())
            listeners.values.flatten().forEach {
                try {
                    it.emit(signal)
                } catch (ex: Exception) {
                    logger.info("Exception while sending KeepAlive signal - {}", ex.message)
                }
            }
        }
    }

    @PreDestroy
    fun shutdown() {
        logger.info("Shutting down DataPublisher scheduler")
        scheduler.shutdown()
    }
}