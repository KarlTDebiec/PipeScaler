#!/bin/bash -ex

# https://drive.google.com/file/d/1TPrz5QKd8DHHt1k8SRtm6tMiPjz_Qene/view?usp=sharing
FILENAME="RRDB_ESRGAN_x4.pth"
FILEID="1TPrz5QKd8DHHt1k8SRtm6tMiPjz_Qene"
curl -c ./cookie -s -L "https://drive.google.com/uc?export=download&id=${FILEID}" > /dev/null
curl -Lb ./cookie "https://drive.google.com/uc?export=download&confirm=`awk '/download/ {print $NF}' ./cookie`&id=${FILEID}" -o ${FILENAME}

# https://drive.google.com/file/d/1MJFgqXJrMkPdKtiuy7C6xfsU1QIbXEb-/view?usp=sharing
FILENAME="RRDB_ESRGAN_x4_old_arch.pth"
FILEID="1MJFgqXJrMkPdKtiuy7C6xfsU1QIbXEb-"
curl -c ./cookie -s -L "https://drive.google.com/uc?export=download&id=${FILEID}" > /dev/null
curl -Lb ./cookie "https://drive.google.com/uc?export=download&confirm=`awk '/download/ {print $NF}' ./cookie`&id=${FILEID}" -o ${FILENAME}

# https://drive.google.com/file/d/1LHplsPRqhmjR28jGgRlEekeP_bvx3nUC/view
FILENAME="1x_BC1-smooth2.pth"
FILEID="1LHplsPRqhmjR28jGgRlEekeP_bvx3nUC"
curl -c ./cookie -s -L "https://drive.google.com/uc?export=download&id=${FILEID}" > /dev/null
curl -Lb ./cookie "https://drive.google.com/uc?export=download&confirm=`awk '/download/ {print $NF}' ./cookie`&id=${FILEID}" -o ${FILENAME}
