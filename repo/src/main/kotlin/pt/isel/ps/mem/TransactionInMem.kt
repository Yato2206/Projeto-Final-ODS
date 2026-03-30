package pt.isel.ps.mem

import pt.isel.ps.RepositoryData
import pt.isel.ps.RepositoryOds
import pt.isel.ps.RepositoryTerms
import pt.isel.ps.Transaction

class TransactionInMem (
    override val repoOds: RepositoryOds,
    override val repoData: RepositoryData,
    override val repoTerms: RepositoryTerms
): Transaction {
    override fun rollback(): Unit = throw UnsupportedOperationException()
}