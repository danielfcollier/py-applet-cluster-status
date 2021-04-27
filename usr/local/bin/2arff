#!/bin/bash 

#Script para converter para o formato arff.
#Os diretorios de entrada sao os locais que contem os arquivos com os parametros de voz.
#Cada diretorio deve conter amostras de apenas um locutor.
#O nome do locutor inserido no arquivo em arff eh o nome do seu diretorio de origem.

#Sobre a arquivo para o Weka:
#A classe do arquivo que deve ser feita a predicao é a primeira. Utilizar o parametro no Weka '-c 1', para especificar a primeira classe.
#Utiliza a maxima memoria heap disponivel.


#Possiveis incrementos:
#Fazer a remoção, caso exita de algum dos arquivos utilizados no script temporariamente.
#Caso seja colocado o caminho completo do diretorio retirar o nome do diretorio para passar como nome do locutor. 
#Caso seja colocado uma barra( / ) apos nome do diretorio, remove-la para realizar o script corretamente.
#Caso sejam colocados parametros excendentes, em ordens diferentes da sugerida ; enviar mensagem de erro. 
#Nao testei o que acontece caso passe por um pipe contendo "echos" de erros. 



#Inicialização das variáveis.
NOME=""
LOCAL=""
OUTPUTFILE=""
CONTADOR=0
contN=0
contO=0
E_BADARGS=65
inDir=""
contI=0

#Verificacoes.

##Verifica o uso correto do primeiro flag.
if [ "$1" != "-d" ]; then 
    echo "Uso: `basename $0` -d <dir1> <dir2> <dir3> ... -n <NUMBER> [-r] -o <out.arff>"
    exit $E_BADARGS
fi

##Verifica se ha o flag '-n' e qual eh o numero de arquivos a serem lidos em cada diretorio.
for i in $*; do
    if [ "$contN" == "1" ]; then
        NUMBER=$i
        #Verifica se o numero e maior que zero.
        if [ $NUMBER -lt 0 ]; then 
            echo "Numero $NUMBER invalido. O numero tem que ser maior que zero."
            exit $E_BADARGS
        fi
        break
    fi
    
    if [ "$i" == "-n" ]; then
        contN=1
    fi
done

##Mensagem de erro para uso incorreto.
if [ "$contN" == "0" ]; then 
    echo "Uso: `basename $0` -d <dir1> <dir2> <dir3> ... -n <NUMBER> [-r] -o <out.arff>"
    exit $E_BADARGS
fi
 
##Identifica os diretorios de entrada.
for i in $*; do
    if [ "$i" == "-n" ]; then
        break;
    fi
    
    if [ $contI == 1 ]; then
        if [ -d $i ]; then
            inDir=$inDir+$i
            inDir=${inDir//+/ }
        else 
            echo $i" nao é um diretorio!"
        fi
    fi
  
    if [ "$i" == "-d" ]; then
        contI=1
    fi
done

##Mensagem de erro para uso incorreto.
if [ "$contI" == "0" ]; then
    echo "Uso: `basename $0` -d <dir1> <dir2> <dir3> ... -n <NUMBER> [-r] -o <out.arff>"
    exit $E_BADARGS
fi

#Verifica se existe(m) diretorios na entrada.
if [ "$inDir" == "" ]; then
    echo "Uso: `basename $0` -d <dir1> <dir2> <dir3> ... -n <NUMBER> [-r] -o <out.arff>"
    exit $E_BADARGS
fi

##Verifica se ha o flag '-o' e qual eh o nome do arquivo de saida.
for i in $*; do
    if [ "$contO" == "1" ]; then
        OUTPUTFILE=$i
        break
    fi
    
    if [ "$i" == "-o" ]; then 
        contO=1
    fi
done

##Mensagem de erro para uso incorreto.
if [ "$contO" == "0" ]; then
    echo "Uso: `basename $0` -d <dir1> <dir2> <dir3> ... -n <NUMBER> [-r] -o <out.arff>"
    exit $E_BADARGS
fi

##Verifica se existe o arquivo de saida.
if [ "$OUTPUTFILE" == "" ]; then
    echo "Uso: `basename $0` -d <dir1> <dir2> <dir3> ... -n <NUMBER> [-r] -o <out.arff>"
    exit $E_BADARGS
fi

##Verifica se existe o arquivo de saida ou o intermediario.
file="$OUTPUTFILE.arff"

if [ -e "$OUTPUTFILE" ]; then 
    echo "$OUTPUTFILE ja existe."
    exit $E_BADARGS
fi

if [ -e $file ]; then 
    echo "$OUTPUTFILE.arff  ja existe."
    exit $E_BADARGS
fi

##Verifica qual a opcao de selecao dos arquivos, aleatoria ou direta.
for i in $*; do
    if [ "$i" == "-r" ]; then
        #Selecao aleatoria.
        opcaoR=0
        break
    else 
        #Selecao direta.
        opcaoR=1
    fi
done

##Verifica se o numero de arquivos pedidos e maior que o numero de arquivos do menor diretorio.
a=0
for i in $inDir; do
    tam[$a]=`ls $i | wc -l`
    if [ $a -gt 0 ]; then
        if [ ${tam[${a}]} -lt $menor ]; then
            menor=${tam[${a}]}
        fi
    else 
        menor=${tam[${a}]}
    fi
    let "a+=1"
done

##Limita o valor de arquivos lidos com o tamanho do menor arquivo.
if [ $NUMBER -gt  $menor ];then 
    NUMBER=$menor
fi

#Selecao dos arquivos.

##Selecao aleatoria.
if [ "$opcaoR" == "0" ]; then
    for i in $inDir; do
        ls $i > temp_$i
        #Define o vetor que contem os arquivos do diretorios como seus elementos.
        k=0
        while read line; do
            vet[${k}]=$line 
            let "k+=1"
        done<temp_$i
        rm -f temp_$i
        #Mostra o numero de arquivos no diretorio.
        let "max=k"
        #Gera um vetor com numeros aletorios. O vetor tem o tamanho do numero de arquivos solicitado.
        for((x=0; x<$NUMBER; x=$((x+1)))); do
            nrandom[x]=$RANDOM
            #Deixa o numero aleatorio no intervalo desejado.
            while [ "${nrandom[$x]}" -gt $max ]; do
                let "nrandom[x]%=max"
            done
            
            echo "${vet[${nrandom[$x]}]}" >> lista_$i
            unset vet[${nrandom[$x]}]
            temp=(`echo ${vet[*]}`)
            unset vet
            vet=(`echo ${temp[*]}`)
            unset temp
            let 'max-=1'
        done
        #Armazena a localizacao do arquivo.
        cd $i
        LOCAL=`pwd`+$LOCAL
        LOCAL=${LOCAL//+/ }
        cd ..
        NOME=lista_$i+$NOME
        NOME=${NOME//+/ }
        CONTADOR=$((CONTADOR+1))
    done 
fi

##Selecao direta. 
if [ "$opcaoR" == "1" ]; then 
    for i in $inDir; do
        #Armazena os arquivos lidos em arquivo temporarios.
        ls $i | head -n $NUMBER > lista_$i
        #Armazena a localizacao do arquivo.
        cd $i
        LOCAL=`pwd`+$LOCAL
        LOCAL=${LOCAL//+/ }
        cd ..
        NOME=lista_$i+$NOME
        NOME=${NOME//+/ } 
        CONTADOR=$((CONTADOR+1))
    done
fi

#Insercao do nome dos locutores.
for i in $inDir; do
    for j in `cat lista_$i`; do
        awk -v LOCUTOR=$i '{ printf "%s %s\n" ,LOCUTOR , $0 }' $i/$j > $i/$j.mod
    done
    ls $i/*.mod > lista_$i
    awk 'BEGIN{FS="/"} {print $2}' lista_$i  > lista_$i.tmp
    mv lista_$i.tmp lista_$i
done

#Executa a concatenacao dos arquivos em um arquivo temporario.
export "LOCAL=$LOCAL"
export "NUMBER=$NUMBER"
export "OUTPUTFILE=$OUTPUTFILE"

awk -v CONTADOR=$CONTADOR 'BEGIN {i=1} {vet1[i]=$0; i++; limite=NR/CONTADOR} END {endereco= ENVIRON["LOCAL"]; split(endereco,end," "); for(i=1;i<=limite;i++) {printf "cat"; for (x=1;x<=CONTADOR;x++) {j[x]=i+(x-1)*limite; a=j[x]; printf " %s/%s",end[x],vet1[a] } printf " >> %s\n" ,ENVIRON["OUTPUTFILE"] } }' $NOME | /bin/bash

#Remover arquivos auxiliares.
for i in $inDir; do  
    rm -f $i/*.mod
    rm -f lista_$i
done

#Coloca nome nos argumentos.
awk '{ i=NF } END{ for(j=1;j<=i;j++){ printf "arg%d ",j } printf "\n" }' $OUTPUTFILE > $OUTPUTFILE.tmp
sed 's/arg1/locutor/' $OUTPUTFILE.tmp >> $OUTPUTFILE

#Gera o arquivo no formato CSV.
sed 's/ / ,/g' $OUTPUTFILE > $OUTPUTFILE.tmp
sed 's/ ,$/ /g' $OUTPUTFILE.tmp > $OUTPUTFILE
   #Gera a lista aleatoria de acordo com o terceiro parametro.
sort -k 3 $OUTPUTFILE > $OUTPUTFILE.tmp
tac $OUTPUTFILE.tmp > $OUTPUTFILE
rm -f $OUTPUTFILE.tmp

#Gera o arquivo no formato ARFF.
    #Utiliza a maxima memoria heap disponivel.
java -mx1024m weka.core.converters.CSVLoader $OUTPUTFILE > $OUTPUTFILE.arff
rm -f $OUTPUTFILE
