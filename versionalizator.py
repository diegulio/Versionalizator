# -*- coding: utf-8 -*-
"""
Spyder Editor

author = Diegulio.
"""

from pymongo import MongoClient
import time
import sys


#%% CONSTANTES
CLUSTER = 'CLUSTER_PATH' # Cluster from Atlas Mongodb
CLIENT = MongoClient(CLUSTER)


#print(client.list_database_names())

# Database
db = CLIENT['versionalizer']  # Database

#print(db.list_collection_names())



#%% Insertar Información en la colección de la  base de datos

# Ejemplo de data 
v1 = {
        'n_version' : 1,
        'name' : 'Nombre Versión',
        'description' : 'Descripción de la versión',
        'todo' : [{'name' : 'to do 1', 
                    'description' : 'descripción to do 1'}],
        #'in_progress' : [], 
        'finished' : [{'name' : 'finished 1',
                       'description' : 'Descripción finished 1'}, 
                      {'name' : 'finished 2',
                       'description' : 'Descripción finished 1'}],
        'assumptions' : [],
        'last_seen' : time.strftime("%a, %d %b %Y %I:%M:%S")
    }


#%% Funciones 

def _input(message, input_type=int):
    '''
    Función para validar inputs del usuario

    Parameters
    ----------
    message : str
        Mensaje a mostrar al usuario.
    message : type
        Tipo de entrada a validar.

    Returns
    -------
    valor del usuario

    '''
    
    while True:
      try:
        return input_type (input(message))
      except:
          print('Sólo se permiten los numeros de las opciones')
    
    
def get_collections(db):
    '''
    Función que devuelve una lista de las colecciones 
    de la base de datos

    Parameters
    ----------
    db : pymongo.database.Database
        Base de datos.

    Returns
    -------
    lista de colecciones de db

    '''
    return db.list_collection_names()


def get_documents(collection, find_dict = None, orderBy_list = None):
    '''
    Función que entrega todos los documentos deseados de una colección de la 
    base de datos ordenados según algún atributo

    Parameters
    ----------
    collection : 
        Colección proyecto .
    find_dict : , optional
        diccionario de elementos a buscar. The default is None.
    orderBy_list : , optional
        lista de orderby's . The default is None.

    Returns
    -------
    Elementos que hacen match. list

    '''
    if find_dict == None:
        if orderBy_list == None:
            return list(collection.find())
        else: 
            return list(collection.find().sort(orderBy_list))
    else:
        if orderBy_list == None:
            return list(collection.find(find_dict))
        else:
            return list(collection.find(find_dict).sort(orderBy_list))
        

def add_activity(n_version, name_act, description_act, col):
    '''
    Función que agrega una nueva actividad a el campo `todo` de 
    ciertas version

    Parameters
    ----------
    n_version : TYPE
        Numero de la version.
    name_act : TYPE
        Nombre de la nueva actividad.
    description_act : TYPE
        Descripción de la nueva actividad.
    col : TYPE
        colección o proyecto dentro de la base de datos.

    Returns
    -------
    None.

    '''
    col.update_one(
        {'n_version' : n_version},
        { '$addToSet': {'todo': {'name': name_act, 'description': description_act}}}
        )
    return None
    

def view_todos(n_version, collection):
    '''
    Función que muestra las tareas por hacer (to do)

    Parameters
    ----------
    n_version : int
        Número de versión.
    collection : TYPE
        Colección de proyecto.

    Returns
    -------
    None.

    '''
    todos_dict = collection.find_one({'n_version':n_version}, {'todo' : 1, '_id':0}) # diccionario {'todo': [lista de todo's]}
    todos = todos_dict['todo']  # lista de todo's
    print("======== To do Activities =========")
    for idx_todo, todo in enumerate(todos):
        print(f'[{idx_todo}] {todo["name"]}')
            
            
            
def todo_to_finished(n_version, collection, idx_activity):
    '''
    Función que mueve una tarea por hacer hacia tarea finalizada.
    Todo -> finished

    Parameters
    ----------
    n_version : Int
        Número Versión.
    collection : TYPE
        Colección de proyecto.
    idx_activity : Ibt
        Id de la actividad a finalizar.

    Returns
    -------
    None.

    '''
    # primero capturo el todo
    act = collection.find_one({'n_version':n_version}, {'todo':1, '_id':0})['todo'][idx_activity]
    name_activity = collection.find_one({'n_version':n_version}, {'todo':1, '_id':0})['todo'][idx_activity]['name']
    
    #Lo agrego a finished (USO $PUSH)
    collection.update_one({'n_version': n_version}, {'$push': {'finished':  act}})
    
    
    
    # Ahora elimino el objeto to do de la lista de todo's (USO $PULL)
    collection.update_one({'n_version': n_version}, {'$pull': {'todo':{'name': name_activity}}})
    
    print(f'Actividad {name_activity} realizada con éxito!')
    


def add_version(version_name, version_desc, collection):
    '''
    Función que agrega una nueva versión (document) al proyecto (colección)

    Parameters
    ----------
    version_name : str
        Nombre de la versión.
    version_desc : str
        Descripción de la versión.
    collection : TYPE
        Colección o proyecto.

    Returns
    -------
    None.

    '''
    
    
    # Encontrar la última version
    # Hago un find de todas las versiones, las ordeno segun n_version de forma ascendente (1), 
    # esto entrega un cursor, el cual lo transformo a lista, obtengo la ultima version, y su atributo n_version
    # Si no se puede significa que no hay versiones anteriores por lo que es la primera
    try:
        n_version = list(collection.find().sort([('n_version',1)]))[-1]['n_version'] + 1
    except:
        n_version = 0
    
    
    # version
    v = {
            'n_version' : n_version,
            'name' : version_name,
            'description' : version_desc,
            'todo' : [],
            #'in_progress' : [], 
            'finished' : [],
            'assumptions' : [],
            'last_seen' : time.strftime("%a, %d %b %Y %I:%M:%S")
        }
    
    # se agrega versión a la colección
    collection.insert_one(v)
    
    print(f"Versión V{n_version} creada exitosamente.")
    
    
    
def first_step():
    """
    Primera etapa : Se le pregunta al usuario para ver
    versiones actuales o para agregar una nueva versión

    Returns
    -------
    None.

    """
    
    print('======================')
    print('[0] Ver versiones')
    print('[1] Agregar nueva versión')
    print('[2] Salir')
    
    while True:
        action = _input("Seleccione : ", int)
        if action in [0,1,2]:
            return action
        else: 
            print('Porfavor agregue una acción válida..')
            
def view_versions(collection_project):
    '''
    Función que muestra al usuario las versiones disponibles
    del proyecto

    Parameters
    ----------
    collection_project : TYPE
        Colección o proyecto.

    Returns
    -------
    TYPE
        Numero de la versión.
    TYPE
        versión (documento).

    '''
    
    
        
    # todos los documentos ordenados de forma ascendente según n_version
    docs = get_documents(collection_project, orderBy_list=[('n_version', 1)])
    
    print('======= versions ========')
    for idx,doc in enumerate(docs):
        print(f'[{idx}] {doc["name"]}')
    print(f'[{len(docs)}] Volver')
        
    while True:
        n_version = _input('Seleccione una versión: ', int)
        if n_version in range(len(docs)):
            version = get_documents(collection_project, find_dict={'n_version' : n_version})[0]
            return n_version, version
        elif n_version == len(docs):
            return None, None
        else:
            print('Porfavor selecciones una versión existente')

def view_version(n_version, version):
    '''
    Función que muestra la información básica
    de una versión

    Parameters
    ----------
    n_version : TYPE
        Numero de la versión.
    version : TYPE
        Versión.

    Returns
    -------
    action : Int
        Siguiente Acción.

    '''
    
    # Se muestra información básica de la version y luego opciones (editar, eliminar, agregar, etc.)
    print("==================================")
    print(f"V{version['n_version']} - {version['name']}")
    print("----------------------------------")
    print(f"{version['description']}")
    print("==================================")
    #print(version)
    
    print('======= Actions ========')
    print('[0] Actividad Realizada') # Pasar una actividad de todo a finished
    print('[1] Nueva Actividad') # Agregar nueva actividad a todo
    #print('[2] Crear version') # Agregar nueva version a la base de datos
    
    while True:
        action = _input('Ingrese acción: ', int)
        if action in [0,1]:
            return action
        else:
            print('Porfavor selecciones una acción válida..')
            
    
    
    
        
            
        
    
    


def main():
    
    global step
    global action
    global collection_project
    '''
    Aplicación Versionalizer

    Returns
    -------
    None.

    '''
    
    ########## Sección Project Selection ################
    
    if step == 'project_selection':
    
        # Primero se muestra la lista de los proyectos que tiene en la base de datos
        projects = get_collections(db) # Lista de proyectos'
        
        print('======= projects ========')
        for idx,project in enumerate(projects):
            print(f'[{idx}] {project}')
        print(f'[{idx+1}] Crear nuevo proyecto') # Para crear nuevo proyecto
        idx_project = _input('Seleccione un proyecto: ', int)
        
        
        if idx_project == idx+1:
            project_name = _input('Nombre del proyecto: ', str)
            # Se debe iniciar con un documento si no, no es posible crear una nueva colección en MongoDB
            version_name = _input('Debe agregar nombre de la primera versión: ', str)
            version_desc = _input('Debe agregar descripción de la primera versión: ', str)
            new_project = db[project_name] # Nueva colección
            add_version(version_name, version_desc, new_project)
            step = 'project_selection'
        else:
            # Se obtiene proyecto desde la base de datos
            collection_project = db[projects[idx_project]]
            step = 'home'
            
            
            
            
        
            
        
        
        
        
    
    
    ########## Sección Home ############
    if step == 'home':
        
        # Una vez escogido, se le da a escoger al usuario "Ver versiones" o "Agregar Nueva versión"
        action = first_step()
    
        if action == 0: # Ver versiones
            step = 'view_versions'
    
        elif action == 1: # Agregar versión
            # Inputs
            version_name = _input('Ingrese nombre de la versión: ', str)
            version_desc = _input('Ingrese descripción de la versión: ', str)
            # Se agrega la nueva versión
            add_version(version_name, version_desc, collection_project)
            # Se vuelve a sección 'Home'
            step = 'home'
        elif action == 2:
            sys.exit()
            
    
    ########## Sección Ver versiones ############
    if step == 'view_versions':
        n_version, version = view_versions(collection_project)
        if n_version == None and version == None:
            step = 'home'
        else:
            step = 'view_version'
    
    ########## Sección Ver versión y Acción ############ 
    if step == 'view_version':
        
        version_action = view_version(n_version, version)
        
        if version_action == 0: # De todo a finished
            
            # Primero mostrar las actividades de todo
            view_todos(n_version, collection_project)
            
            # To do que se ha realizado
            todo_check = _input("Ingrese Id de la actividad realizada: ", int)
            
            # Envío to do a finished
            todo_to_finished(n_version, collection_project, todo_check)
            step = 'view_versions' # Se vuelve a ver las versiones
            
        elif version_action == 1:  # Agregar actividad
            
            name_activity = input('Ingrese nombre de la actividad: ')
            description_activity = input('Ingrese una descripción de la actividad: ')
            add_activity(n_version, name_activity, description_activity, collection_project)
            step = 'view_versions' # Se vuelve a ver las versiones
        
    


        
        
        
        
        
    
        
    
        

        
    
    
    
    

    
        
    
    
    
    
    

#%% MAIN

step = 'project_selection' # Primera sección
if __name__ == '__main__':
    
    while True:    
        main()
    


