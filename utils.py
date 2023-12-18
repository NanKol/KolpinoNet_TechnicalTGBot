"""Внешнии функции"""
import asyncio
import logging
import db


async def getobjectname(cursor, objid) -> str:
    """Возвращает полный адрес"""
    
    if (int(objid) > 0):
        await cursor.execute(db.get_street_elm.format(objid = objid))
        
        rows = await cursor.fetchall()
        for curobj in rows:
            fulladdr = await getstreet(cursor, curobj['street']) + ", дом " + curobj['dom']
            if(len(curobj['korp']) > 0):
                fulladdr += f", корп {curobj['korp']}"
            return fulladdr


async def getstreet(cursor, streetid) -> str:
    """Возращает улицу"""
    
    if (int(streetid) > 0):
        await cursor.execute(db.get_street.format(streetid = streetid))
        
        rows = await cursor.fetchall()
        
        for currstreet in rows:
            strname = currstreet['cityname'] + ", " + currstreet['street']
            if (len(currstreet['streettype']) > 0):
                    strname += " " + currstreet['streettype']
            return strname
