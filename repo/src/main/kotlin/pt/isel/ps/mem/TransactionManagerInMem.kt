package pt.isel.ps.mem

import pt.isel.ps.Transaction
import pt.isel.ps.TransactionManager

class TransactionManagerInMem : TransactionManager {
    private val repoOds = RepositoryOdsInMem()
    private val repoData = RepositoryDataInMem()
    private val repoTerms = RepositoryTermsInMem()

    override fun <R> run(block: Transaction.() -> R): R =
        block(TransactionInMem(repoOds, repoData, repoTerms))
}