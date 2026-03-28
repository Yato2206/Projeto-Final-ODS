package jdbc.pt.isel.ps

import pt.isel.ps.Transaction
import java.sql.Connection

class TransactionJdbc(
    private val con: Connection,
) : Transaction {
    override val repoData = RepositoryDataJdbc(con)
    override val repoTerms = RepositoryTermsJdbc(con)
    override val repoOds = RepositoryOdsJdbc(con)


    override fun rollback() {
        con.rollback()
    }
}