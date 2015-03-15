#!/bin/sh
scriptdir=`dirname $0`

~/java/jre8/bin/java -mx2500m -cp "$scriptdir/stanford-ner.jar:" edu.stanford.nlp.ie.crf.CRFClassifier -loadClassifier $scriptdir/classifiers/dewac_175m_600.crf.ser.gz -textFile $1
