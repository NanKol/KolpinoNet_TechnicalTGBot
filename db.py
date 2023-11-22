search_truble = """SELECT
             t.id as tid,
             UNIX_TIMESTAMP(t.date_start) as date_start,
             UNIX_TIMESTAMP(t.date_end) as date_end,
             e.brand,e.model,e.ipaddr,e.comment as ecomment,
             t.objid,
             ond.location,
             t.comment,
             a.adm_fullname,
             t.eqid,
             t.plan,
             UNIX_TIMESTAMP(t.plan_time) as plan_time
           FROM troubles as t
             LEFT JOIN admins as a ON (a.adm_id=t.openadm)
             LEFT JOIN equipment as e ON (e.id=t.eqid)
             LEFT JOIN objects as o ON (o.id=t.objid)
             LEFT JOIN objects_nodes as ond ON (ond.id=t.nodeid)
           WHERE e.online=0 AND t.date_end=0 AND t.sent2tgm=0"""


count_user1 = """SELECT  COUNT(*) AS fl FROM equipment_ports AS ep.
                LEFT JOIN users_services AS us ON (us.id=ep.serviceid)
                LEFT JOIN users AS u ON (us.uid=u.id)
                WHERE ep.eqid=".$trb['eqid']." AND ep.porttype!='FREE' AND u.cli_type=0"""


count_user2 = """SELECT  COUNT(*) AS yl FROM equipment_ports AS ep.
                LEFT JOIN users_services AS us ON (us.id=ep.serviceid)
                LEFT JOIN users AS u ON (us.uid=u.id)
                WHERE ep.eqid=".$trb['eqid']." AND ep.porttype!='FREE' AND u.cli_type=1"""