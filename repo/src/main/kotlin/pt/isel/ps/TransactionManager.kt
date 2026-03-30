package pt.isel.ps

interface TransactionManager {
    /**
     * This method creates an instance of pt.isel.ps.Transaction, potentially
     * initializing a JDBC Connection,a JDBI Handle, or another resource,
     * which is then passed as an argument to the pt.isel.ps.Transaction constructor.
     */
    fun <R> run(block: Transaction.() -> R): R
}