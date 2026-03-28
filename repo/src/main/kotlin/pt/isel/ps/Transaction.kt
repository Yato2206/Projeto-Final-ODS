package pt.isel.ps

/**
 * The lifecycle of a pt.isel.ps.Transaction is managed outside the scope of the IoC/DI container.
 * Transactions are instantiated by a pt.isel.ps.TransactionManager,
 * which is managed by the IoC/DI container (e.g., Spring).
 * The implementation of pt.isel.ps.Transaction is responsible for creating the
 * necessary repository instances in its constructor.
 */
interface Transaction {
    val repoOds: RepositoryOds
    val repoTerms: RepositoryTerms
    val repoData: RepositoryData

    fun rollback()
}