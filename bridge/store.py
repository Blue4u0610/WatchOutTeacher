import json
import re
import sqlite3
import uuid
from common import DATA, AppError, require, short_text

DEFAULTS={'primary':'codex','fallback':True,'codex_model':'','claude_model':'','codex_effort':'','timeout':90,'active_course':None}

class Store:
    def __init__(self, directory=DATA):
        self.directory=directory
        directory.mkdir(mode=0o700,parents=True,exist_ok=True)
        self.path=directory/'courses.sqlite3'
        with self.db() as db:
            db.executescript('''
            PRAGMA journal_mode=WAL;
            CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY,value TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS courses(id TEXT PRIMARY KEY,name TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS documents(id TEXT PRIMARY KEY,course TEXT NOT NULL REFERENCES courses(id) ON DELETE CASCADE,name TEXT NOT NULL,status TEXT NOT NULL,warnings TEXT NOT NULL,created TEXT DEFAULT CURRENT_TIMESTAMP);
            CREATE TABLE IF NOT EXISTS chunks(id INTEGER PRIMARY KEY,document TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,number INTEGER NOT NULL,kind TEXT NOT NULL,text TEXT NOT NULL);
            CREATE INDEX IF NOT EXISTS chunks_document ON chunks(document);
            CREATE VIRTUAL TABLE IF NOT EXISTS search USING fts5(text,content='chunks',content_rowid='id',tokenize='unicode61');
            CREATE TRIGGER IF NOT EXISTS chunks_ai AFTER INSERT ON chunks BEGIN INSERT INTO search(rowid,text) VALUES(new.id,new.text); END;
            CREATE TRIGGER IF NOT EXISTS chunks_ad AFTER DELETE ON chunks BEGIN INSERT INTO search(search,rowid,text) VALUES('delete',old.id,old.text); END;
            CREATE TABLE IF NOT EXISTS diagnostics(id INTEGER PRIMARY KEY,time TEXT DEFAULT CURRENT_TIMESTAMP,request TEXT,provider TEXT,code TEXT,details TEXT);
            ''')
        self.path.chmod(0o600)

    def db(self):
        db=sqlite3.connect(str(self.path),timeout=10)
        db.row_factory=sqlite3.Row
        db.execute('PRAGMA foreign_keys=ON')
        return db

    def settings(self):
        with self.db() as db: return {**DEFAULTS,**{r['key']:json.loads(r['value']) for r in db.execute('SELECT * FROM settings')}}

    def save_settings(self, values):
        allowed={'primary','fallback','codex_model','claude_model','codex_effort','timeout'}
        require(set(values)<=allowed,'不支持的设置字段。')
        if 'primary' in values: require(values['primary'] in ['codex','claude'],'主 Provider 无效。')
        if 'fallback' in values: require(isinstance(values['fallback'],bool),'备用开关无效。')
        if 'timeout' in values: require(type(values['timeout']) is int and 20<=values['timeout']<=180,'总超时须为 20–180 秒。')
        if 'codex_effort' in values: require(isinstance(values['codex_effort'],str) and values['codex_effort'] in ['', 'none','minimal','low','medium','high','xhigh','max'],'推理强度无效。')
        for key in ['codex_model','claude_model']:
            if key in values: require(isinstance(values[key],str) and re.fullmatch(r'(?:[a-zA-Z0-9][a-zA-Z0-9._:/-]{0,99})?',values[key]) is not None,'模型名称格式无效。')
        with self.db() as db:
            for key,value in values.items(): db.execute('INSERT OR REPLACE INTO settings VALUES(?,?)',(key,json.dumps(value)))
        return self.settings()

    def state(self):
        with self.db() as db:
            courses=[dict(r) for r in db.execute('SELECT * FROM courses ORDER BY rowid')]
            documents=[{**dict(r),'warnings':json.loads(r['warnings'])} for r in db.execute('SELECT d.*,count(c.id) chunks FROM documents d LEFT JOIN chunks c ON c.document=d.id GROUP BY d.id ORDER BY d.created,d.rowid')]
        return {'courses':courses,'documents':documents,'settings':self.settings()}

    def course_exists(self, course):
        with self.db() as db: require(db.execute('SELECT 1 FROM courses WHERE id=?',(course,)).fetchone() is not None,'课程不存在，请重新选择。')

    def create(self,name):
        name=short_text(name,100,'课程名称'); cid=str(uuid.uuid4())
        with self.db() as db:
            require(db.execute('SELECT count(*) FROM courses').fetchone()[0]<100,'最多支持 100 门课程。')
            db.execute('INSERT INTO courses VALUES(?,?)',(cid,name))
            db.execute('INSERT OR REPLACE INTO settings VALUES(?,?)',('active_course',json.dumps(cid)))
        return self.state()

    def rename(self,cid,name):
        self.course_exists(cid); name=short_text(name,100,'课程名称')
        with self.db() as db: db.execute('UPDATE courses SET name=? WHERE id=?',(name,cid))
        return self.state()

    def select(self,cid):
        if cid is not None: self.course_exists(cid)
        with self.db() as db: db.execute('INSERT OR REPLACE INTO settings VALUES(?,?)',('active_course',json.dumps(cid)))
        return self.state()

    def delete(self,cid):
        with self.db() as db:
            db.execute('DELETE FROM courses WHERE id=?',(cid,))
            active=db.execute("SELECT value FROM settings WHERE key='active_course'").fetchone()
            if active and json.loads(active[0])==cid: db.execute("DELETE FROM settings WHERE key='active_course'")
        return self.state()

    def remove(self,doc):
        with self.db() as db: db.execute('DELETE FROM documents WHERE id=?',(doc,))
        return self.state()

    def add(self,course,name,parsed=None,failure=None):
        self.course_exists(course); did=str(uuid.uuid4()); chunks=[]
        if parsed:
            for unit in parsed['units']:
                text=unit['text'].strip()
                for offset in range(0,len(text),1600):
                    if text[offset:offset+1800].strip(): chunks.append((did,unit['number'] if unit['kind']!='text' else offset//1600+1,unit['kind'],text[offset:offset+1800]))
        with self.db() as db:
            count=db.execute('SELECT count(*) FROM chunks c JOIN documents d ON c.document=d.id WHERE d.course=?',(course,)).fetchone()[0]
            require(count+len(chunks)<=20000,'每门课程最多 20,000 个片段，请移除资料或拆分课程；此次未导入。')
            require(db.execute('SELECT count(*) FROM documents WHERE course=?',(course,)).fetchone()[0]<300,'每门课程最多 300 份资料。')
            warnings=[failure] if failure else parsed['warnings']
            db.execute('INSERT INTO documents(id,course,name,status,warnings) VALUES(?,?,?,?,?)',(did,course,name,'error' if failure else 'ready',json.dumps(warnings)))
            db.executemany('INSERT INTO chunks(document,number,kind,text) VALUES(?,?,?,?)',chunks)
        return self.state()

    def retrieve(self,course,query):
        if course is None: return [],{'selected':0,'total':0,'reason':'未选择课程'},[]
        self.course_exists(course)
        with self.db() as db:
            total=db.execute('SELECT count(*) FROM chunks c JOIN documents d ON c.document=d.id WHERE d.course=?',(course,)).fetchone()[0]
            docs=db.execute('SELECT name,status,warnings FROM documents WHERE course=?',(course,)).fetchall()
            all_words=list(dict.fromkeys(re.findall(r'[\w]+',query.lower())))
            words=all_words[:48]
            rows=[]
            if words:
                match=' OR '.join('"'+w.replace('"','""')+'"' for w in words)
                rows=db.execute('SELECT c.*,d.name FROM search JOIN chunks c ON c.id=search.rowid JOIN documents d ON d.id=c.document WHERE search MATCH ? AND d.course=? ORDER BY bm25(search) LIMIT 12',(match,course)).fetchall()
            no_match=not rows
            if not rows:
                rows=db.execute('SELECT c.*,d.name FROM chunks c JOIN documents d ON d.id=c.document WHERE d.course=? ORDER BY c.id LIMIT 12',(course,)).fetchall()
        excerpts=[{'source_id':f'S{i+1}','document_id':r['document'],'document':r['name'],'page_or_slide':r['number'],'kind':r['kind'],'text':r['text']} for i,r in enumerate(rows)]
        warnings=[]
        if len(all_words)>48: warnings.append('检索查询超过 48 个不同词；仅使用前 48 个词，完整题目仍提供给模型。')
        if total>len(rows): warnings.append(f'本题选用 {len(rows)}/{total} 个资料片段，未覆盖整门课程。')
        if no_match and total: warnings.append('关键词未命中，使用资料开头片段；跨语言检索可能漏检。')
        for doc in docs:
            if doc['status']=='error': warnings.append(f'{doc["name"]} 导入失败，未参与检索。')
            elif json.loads(doc['warnings']): warnings.append(f'{doc["name"]} 存在解析限制，详见资料列表。')
        return excerpts,{'selected':len(excerpts),'total':total,'reason':'first_chunks' if no_match else 'fts5_bm25','query_terms':len(words),'query_terms_total':len(all_words),'query_terms_truncated':len(all_words)>48},warnings[:15]

    def log(self,rid,provider,code,details):
        with self.db() as db:
            db.execute('INSERT INTO diagnostics(request,provider,code,details) VALUES(?,?,?,?)',(rid,provider,code,json.dumps(details)))
            db.execute('DELETE FROM diagnostics WHERE id NOT IN (SELECT id FROM diagnostics ORDER BY id DESC LIMIT 100)')

    def diagnostics(self):
        with self.db() as db: return [dict(r) for r in db.execute('SELECT * FROM diagnostics ORDER BY id DESC LIMIT 50')]
