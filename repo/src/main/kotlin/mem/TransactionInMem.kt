package mem

import RepositoryData
import RepositoryOds
import RepositoryTerms
import Transaction

class TransactionInMem (
    override val repoOds: RepositoryOds,
    override val repoData: RepositoryData,
    override val repoTerms: RepositoryTerms
): Transaction {
    override fun rollback(): Unit = throw UnsupportedOperationException()
}