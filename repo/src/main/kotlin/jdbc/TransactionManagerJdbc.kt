package jdbc

import Transaction
import TransactionManager

class TransactionManagerJdbc : TransactionManager {
    override fun <R> run(block: Transaction.() -> R): R =
        DatabaseConnection.getConnection().use { con ->
            try {
                val tx = TransactionJdbc(con)
                val result = block(tx)
                con.commit()
                result
            } catch (e: Exception) {
                con.rollback()
                throw e
            }
        }
}