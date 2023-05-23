      SUBROUTINE HETVAL(CMNAME,TEMP,TIME,DTIME,STATEV,FLUX,
     1 PREDEF,DPRED)
C
      INCLUDE 'ABA_PARAM.INC'
C
      CHARACTER*80 CMNAME
C
      DIMENSION TEMP(2),STATEV(*),PREDEF(*),TIME(2),FLUX(2),
     1 DPRED(*)
C
      REAL TL, TLPREV, TL0, TLEQ, KL, RL, FALPH_PREV, FALPH_CUR, TLINC
C     
C     Initialize Variables
      TL0=0.3
      KL=1.42
      RL=294.0
C
C     Set flux to zero needed by HETVAL subroutine
      FLUX(1)=0.0
C
C     
C     Initizializes TLPREV
      IF (STATEV(20).EQ.0.0) THEN
            TLPREV=TL0
      ELSE
            TLPREV=STATEV(20)
      END IF
C
C     SDV 4 containst the current alpha phase fraction calculated by Abaqus
      FALPH_PREV = STATEV(18)
      FALPH_CUR = STATEV(4)
      FALPH_INC = FALPH_CUR-FALPH_PREV
C
C     
      TLEQ = KL*EXP(-1.0*RL/(TEMP(1)+273.0))
C
      IF (FALPH_CUR.LE.0.01) THEN
            TL = TL0
      ELSE
C            TL = (TLPREV-TLEQ)*(FALPH_PREV/FALPH_CUR)+TLEQ
C
            TLINC = (TLPREV*FALPH_CUR + TLEQ*FALPH_INC)/(FALPH_CUR+FALPH_INC)-TLPREV
            TL = TLPREV+TLINC    
C
C           Adds a factor that depends on time increment and current temperature, useful for heat treatments
C            IF (TEMP(1).GT.800) THEN
C                  TL = TL + 0.00000001 * TIME(2) * TEMP(1)
C            END IF
      END IF
C
C     Saving FALPH_CUR in SDV18
      STATEV(18) = FALPH_CUR
C
C     Saving calculated lath thickness in SDV20
      STATEV(20) = TL
C
      RETURN
      END


