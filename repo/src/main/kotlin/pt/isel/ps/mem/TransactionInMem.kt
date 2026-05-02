package pt.isel.ps.mem

import pt.isel.ps.RepositoryAnalysis
import pt.isel.ps.RepositoryData
import pt.isel.ps.RepositoryDocument
import pt.isel.ps.RepositoryOds
import pt.isel.ps.RepositoryTerms
import pt.isel.ps.Transaction

class TransactionInMem (
    override val repoOds: RepositoryOds,
    override val repoData: RepositoryData,
    override val repoTerms: RepositoryTerms,
    override val repoDocument: RepositoryDocument,
    override val repoAnalysis: RepositoryAnalysis,
): Transaction {
    override fun rollback(): Unit = throw UnsupportedOperationException()
}