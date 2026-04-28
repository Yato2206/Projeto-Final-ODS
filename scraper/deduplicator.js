const fs = require('fs');
const path = require('path');

/**
 * Script para:
 * 1. Ler todos os ficheiros repo_cientifico_*.json
 * 2. Eliminar duplicados
 * 3. Reorganizar em ficheiros com 1000 items cada (ORDENADOS por data)
 * 4. Eliminar ficheiros antigos
 * 5. Ignorar items com título "Sem título"
 */

// Função para extrair data de dataPublicacao (formato: "yyyy-mm-dd", "yyyy-mm" ou "yyyy")
function parseDataPublicacao(dataStr) {
    if (!dataStr) return { dia: 0, mes: 0, ano: 0, dataTermos: 0 };

    const parts = dataStr.split('-');
    if (parts.length === 3) {
        // Formato: "yyyy-mm-dd" (dataTermos máxima = 3)
        return {
            dia: parseInt(parts[2]) || 0,
            mes: parseInt(parts[1]) || 0,
            ano: parseInt(parts[0]) || 0,
            dataTermos
            : 3
        };
    } else if (parts.length === 2) {
        // Formato: "yyyy-mm" (dataTermos = 2)
        return {
            dia: 0,
            mes: parseInt(parts[1]) || 0,
            ano: parseInt(parts[0]) || 0,
            dataTermos: 2
        };
    } else if (parts.length === 1) {
        // Formato: "yyyy" (dataTermos = 1)
        return { dia: 0, mes: 0, ano: parseInt(parts[0]) || 0, dataTermos: 1 };
    }
    return { dia: 0, mes: 0, ano: 0, dataTermos: 0 };
}

// Função para comparar datas (descendente - mais recente primeiro)
function compararDatas(a, b) {
    const dataA = parseDataPublicacao(a[1].dataPublicacao);
    const dataB = parseDataPublicacao(b[1].dataPublicacao);

    // 1. PRIORIDADE: Comparar por ano (descendente - 2026 antes de 2025)
    if (dataA.ano !== dataB.ano) return dataB.ano - dataA.ano;
    
    // 2. Se dataTermos igual, comparar por mês (descendente)
    if (dataA.mes !== dataB.mes) return dataB.mes - dataA.mes;

    // 3. Se mês igual, comparar por dia (descendente)
    if (dataA.dia !== dataB.dia) return dataB.dia - dataA.dia;

    // 4. Se ano igual, comparar por dataTermos (descendente - data mais completa primeiro)
    //    dd-mm-yyyy (3) > mm-yyyy (2) > yyyy (1)
    if (dataA.dataTermos !== dataB.dataTermos) return dataB.dataTermos - dataA.dataTermos;

    // 5. Se tudo igual, usar dateChecked
    const dateA = new Date(a[1].dateChecked || 0);
    const dateB = new Date(b[1].dateChecked || 0);
    return dateB - dateA;
}

async function deduplicateAndReorganize() {
    console.log('\n' + '='.repeat(80));
    console.log('DEDUPLICADOR E REORGANIZADOR');
    console.log('='.repeat(80) + '\n');

    try {
        console.log('Passo 1: Procurando ficheiros repo_cientifico_*.json...');

        const files = fs.readdirSync('.')
            .filter(f => f.match(/^repo_cientifico_\d+\.json$/))
            .sort((a, b) => {
                const numA = parseInt(a.match(/\d+/)[0]);
                const numB = parseInt(b.match(/\d+/)[0]);
                return numA - numB;
            });

        console.log(`Encontrados ${files.length} ficheiros\n`);

        if (files.length === 0) {
            console.error('Nenhum ficheiro encontrado!');
            return;
        }

        console.log('Passo 2: Carregar os dados e eliminar os duplicados...');

        const allData = {};
        let totalBefore = 0;
        let duplicatesFound = 0;
        let ignoredItems = 0;

        for (const file of files) {
            try {
                const data = JSON.parse(fs.readFileSync(file, 'utf-8'));

                const itemsBefore = Object.keys(data).length;
                totalBefore += itemsBefore;

                for (const [key, value] of Object.entries(data)) {
                    // Ignorar items com título "Sem título"
                    if (value.titulo === "Sem título") {
                        ignoredItems++;
                        continue;
                    }

                    if (allData[key]) {
                        duplicatesFound++;
                    } else {
                        allData[key] = value;
                    }
                }

                const itemsAdded = Object.keys(data).length - duplicatesFound;
                console.log(` ${file}: ${itemsBefore} items (${itemsAdded} novos, ${duplicatesFound} duplicados)`);

            } catch (error) {
                console.error(` Erro ao ler ${file}: ${error.message}`);
            }
        }

        const totalAfter = Object.keys(allData).length;
        console.log(`\nTotal antes: ${totalBefore} items`);
        console.log(`Total após deduplicação: ${totalAfter} items`);
        console.log(`Duplicados eliminados: ${totalBefore - totalAfter}`);
        console.log(`Items "Sem título" ignorados: ${ignoredItems}\n`);

        console.log('Passo 3: Reorganizando em ficheiros com 1000 items (ordenados por data)...');

        let entries = Object.entries(allData);

        // Ordenar por data (descendente - mais recente primeiro)
        entries.sort(compararDatas);

        const ITEMS_PER_FILE = 1000;
        const numFiles = Math.ceil(entries.length / ITEMS_PER_FILE);

        console.log(`Número de ficheiros necessários: ${numFiles}\n`);

        let fileIndex = 1;

        for (let i = 0; i < entries.length; i += ITEMS_PER_FILE) {
            const chunk = entries.slice(i, i + ITEMS_PER_FILE);
            const chunkData = Object.fromEntries(chunk);

            const newFilename = `repo_cientifico_${fileIndex}.json`;
            fs.writeFileSync(newFilename, JSON.stringify(chunkData, null, 2), 'utf-8');

            console.log(`${newFilename}: ${chunk.length} items`);
            fileIndex++;
        }

        console.log('\nPasso 4: Eliminando ficheiros antigos...');

        for (const file of files) {
            const fileNum = parseInt(file.match(/\d+/)[0]);
            if (fileNum >= numFiles + 1) {
                fs.unlinkSync(file);
                console.log(`Eliminado: ${file}`);
            }
        }

        console.log('\n' + '='.repeat(80));
        console.log('REORGANIZAÇÃO COMPLETA!');
        console.log('='.repeat(80));
        console.log(`\nResumo:`);
        console.log(`  • Ficheiros originais: ${files.length}`);
        console.log(`  • Ficheiros novos: ${numFiles}`);
        console.log(`  • Total de items (sem duplicados): ${totalAfter}`);
        console.log(`  • Duplicados eliminados: ${totalBefore - totalAfter}`);
        console.log(`  • Items "Sem título" ignorados: ${ignoredItems}`);
        console.log(`  • Items por ficheiro: 1000 (último pode ter menos)`);
        console.log('\n');

    } catch (error) {
        console.error('Erro fatal:', error.message);
    }
}

deduplicateAndReorganize();

