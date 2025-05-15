from ldap3 import Server, Connection, ALL, SUBTREE, BASE
from ldap3.core.exceptions import LDAPException
from models import db, LdapObject, AuthSource


def connect_to_ldap(host, bind_dn, password, timeout=5, port=389, ssl=False):
    """
    Establish a connection to the LDAP server.
    """
    try:
        server = Server(host, get_info=ALL, connect_timeout=timeout, port=port, use_ssl=ssl)
        connection = Connection(server, user=bind_dn, password=password, auto_bind=False)
        # loggie(level="INFO", message="Successfully connected to ldap server", data={'ldap': str(connection)})
        return connection
    except LDAPException as e:
        print(f"Failed to connect to LDAP server: {e}")
        loggie(level="ERROR", message="Error connecting to ldap", data={'error': str(e)})

        return None
    
# def bind_to_ldap(host, bind_user_dn, bind_user_password, timeout=5, port=389, ssl=False):
#     ldap = connect_to_ldap(host, bind_user_dn, bind_user_password, timeout=timeout, port=port, ssl=ssl)
#     if not ldap:
#         return False
#     if not ldap.bind():
#         return False
#     return ldap
    
def validate_credentials(host, connection, base_dn, username, password, is_ad, port=389, ssl=False, timeout=5):
    """
    Validate a username and password against the LDAP/AD server.
    """
    result = search_ldap(connection, base_dn, is_ad, username=username)
    if len(result) >= 1:
        try:
            server = Server(host, get_info=ALL, connect_timeout=timeout, port=port, use_ssl=ssl)
            with Connection(server, user=result[0]['dn'], password=password) as conn:
                # print(conn.result["description"])
                print(username)
                data = search_ldap(connection=connection, base_dn=base_dn, is_ad=is_ad, username=username)
                return { 'success': True, 'data': data}
        except Exception as e:
            print(e)
            print(f'Unable to connect to LDAP server: {str(e)}')
    return { 'success': False, 'data': None}




def search_ldap(connection, base_dn, is_ad, search_type="all", query=None, uuid=None, username=None):
    """
    Search LDAP/AD for users and/or groups with optional filters for UUID, username, or custom queries.
    Combines user/group filters with OR and other filters (uuid, username, query) with AND.
    """
    # Define attributes to request based on server type
    if is_ad:
        attributes = ['cn', 'sAMAccountName', 'objectGUID', 'objectClass']
    else:
        attributes = ['cn', 'uid', 'entryUUID', 'objectClass', 'uidNumber', 'gidNumber']

    # Base filters for users and groups
    user_filter = "(objectClass=person)" if is_ad else "(objectClass=inetOrgPerson)"
    group_filter = "(objectClass=group)" if is_ad else "(objectClass=posixGroup)"

    # Apply the search_type filter
    if search_type == "user":
        base_filter = user_filter
    elif search_type == "group":
        base_filter = group_filter
    else:  # "all"
        base_filter = f"(|{user_filter}{group_filter})"

    # Additional filters to AND with the base filter
    additional_filters = []

    if uuid:
        additional_filters.append(f"(objectGUID={uuid})" if is_ad else f"(entryUUID={uuid})")

    if username:
        additional_filters.append(f"(sAMAccountName={username}*)" if is_ad else f"(uid={username}*)")

    if query:
        additional_filters.append(f"(cn=*{query}*)")

    # Combine all filters with AND
    if additional_filters:
        search_filter = f"(&{base_filter}{''.join(additional_filters)})"
    else:
        search_filter = base_filter

    # Perform the search with requested attributes
    connection.search(base_dn, search_filter, search_scope=SUBTREE, attributes=attributes)
    # Process and clean results
    results = []
    for entry in connection.entries:
        entry_dict = entry.entry_attributes_as_dict
        object_classes = entry_dict.get('objectClass', [])

        # Determine the type based on objectClass
        entry_type = "user" if any(cls in object_classes for cls in ['person', 'inetOrgPerson']) else "group"

        # Set ID and UUID based on the entry type
        if entry_type == "user":
            id_value = entry_dict.get('sAMAccountName', [None])[0] if is_ad else entry_dict.get('uid', [None])[0]
            uuid_value = str(entry_dict.get('objectGUID', [None])[0]).strip('{}') if is_ad else entry_dict.get('entryUUID', [None])[0]
            try:
                if is_ad:
                    # AD uses objectGUID for unique identifiers
                    uid = str(entry_dict.get('objectGUID', [None])[0]).strip('{}')
                else:
                    # OpenLDAP prefers uidNumber if available
                    uid = entry_dict.get('uidNumber', [None])[0]
            except:
                uid = None
        else:
            id_value = entry_dict.get('cn', [None])[0]
            uuid_value = str(entry_dict.get('objectGUID', [None])[0]).strip('{}') if is_ad else entry_dict.get('entryUUID', [None])[0]
            try:
                if is_ad:
                    uid = str(entry_dict.get('objectGUID', [None])[0]).strip('{}')
                else:
                    # OpenLDAP prefers gidNumber for groups
                    uid = entry_dict.get('gidNumber', [None])[0]
            except:
                uid = None
            
        results.append({
            "id": id_value,
            "uid": uid,
            "dn": entry.entry_dn.strip(),
            "uuid": uuid_value,
            "name": entry_dict.get('cn', [None])[0],
            "type": entry_type
        })

    return results



# Function to get all groups a user is in from User UUID
def get_user_groups(connection, base_dn, user_uuid, is_ad, cascade=False):
    """
    Retrieve all groups a user is in based on the user's UUID (objectGUID for AD, entryUUID for OpenLDAP).
    Returns a list of group UUIDs.
    """
    # Get the user's DN
    user_info = search_ldap(connection, base_dn, uuid=user_uuid, is_ad=is_ad)
    if not user_info:
        return []

    user_dn = user_info[0]['dn']
    # print(user_dn)
    # Define the group search filter and attributes based on the server type
    if is_ad:
        # For AD, search for groups where the user DN is a member
        search_filter = f"(member={user_dn})"
        attributes = ['objectGUID']
    else:
        # For OpenLDAP, search for groups where the user UID or UID Number is a memberUid
        # print(user_info[0])
        search_filter = f"(|(memberUid={user_info[0]['id']})(memberUid={user_info[0]['uid']}))"
        attributes = ['entryUUID']

    # Perform the group search
    connection.search(base_dn, search_filter, search_scope=SUBTREE, attributes=attributes)
    # Extract the group UUIDs
    direct_groups = []
    for entry in connection.entries:
        if is_ad:
            direct_groups.append(str(entry['objectGUID'].value).strip('{}'))
        else:
            direct_groups.append(entry['entryUUID'].value)

    # If cascade is enabled, recursively find all nested groups
    if cascade and len(direct_groups) > 0:
        all_groups_uuid = search_ldap(connection, base_dn, is_ad, search_type="group")
        visited = set(direct_groups)
        groups_to_process = direct_groups[:]

        while groups_to_process:
            current_group_uuid = groups_to_process.pop()

            # Get the group's direct members
            group = search_ldap(connection, base_dn, uuid=current_group_uuid, is_ad=is_ad)
            if group:
                group_dn = group[0]['dn']
                if is_ad:
                    # For AD, search for groups where the user DN is a member
                    search_filter = f"(member={group_dn})"
                    attributes = ['objectGUID']
                else:
                    print("Cascade groups are not implemented on not ad like ldap servers")
                    # # For OpenLDAP, search for groups where the user UID or UID Number is a memberUid
                    # # print(user_info[0])
                    # search_filter = f"(|(memberUid={group[0]['id']})(memberUid={group[0]['uid']}))"
                    # attributes = ['entryUUID']

                # Perform the group search
                connection.search(base_dn, search_filter, search_scope=SUBTREE, attributes=attributes)
                for nested_entry in connection.entries:
                    if is_ad:
                        nested_uuid = str(nested_entry['objectGUID'].value).strip('{}')
                    else:
                        nested_uuid = nested_entry['entryUUID'].value

                    # Add to visited and process queue if not already processed
                    if nested_uuid not in visited:
                        visited.add(nested_uuid)
                        groups_to_process.append(nested_uuid)

        return list(visited)

    return direct_groups

# Function to get all groups a user is in from User UUID
def get_group_members(connection, base_dn, group_uuid, is_ad):
    """
    Retrieve all members of a group based on the group's UUID (objectGUID for AD, entryUUID for OpenLDAP).
    Returns a list of member UUIDs.
    """
    # Search for the group by UUID
    group_filter = f"(objectGUID={group_uuid})" if is_ad else f"(entryUUID={group_uuid})"
    group_attributes = ['member'] if is_ad else ['memberUid']

    # Search for the group
    connection.search(base_dn, group_filter, search_scope=SUBTREE, attributes=group_attributes)

    if not connection.entries:
        return []

    # Extract member values
    members = connection.entries[0]['member'].values if is_ad else connection.entries[0]['memberUid'].values

    member_uuids = []

    # Process members based on server type
    for member in members:
        if is_ad:
            # For AD, search by DN to get the UUID
            connection.search(member, '(objectClass=*)', search_scope=BASE, attributes=['objectGUID'])
            if connection.entries:
                uuid_value = str(connection.entries[0]['objectGUID'].value).strip('{}')
                member_uuids.append(uuid_value)
        else:
            # For OpenLDAP, search by UID or UID Number to get the entryUUID
            # First, try searching by UID
            search_filter = f"(|(uid={member})(uidnumber={member}))"
            connection.search(base_dn, search_filter, search_scope=SUBTREE, attributes=['entryUUID'])
            # print(connection.entries)
            if connection.entries:
                uuid_value = connection.entries[0]['entryUUID'].value
                member_uuids.append(uuid_value)
            # else:
            #     # If no result with UID, try searching by UID Number
            #     search_filter = f"(uidNumber={member})"
            #     connection.search(base_dn, search_filter, search_scope=SUBTREE, attributes=['entryUUID'])
            #     if connection.entries:
            #         uuid_value = connection.entries[0]['entryUUID'].value
            #         member_uuids.append(uuid_value)

    return member_uuids


def handle_ldap_object(uuid, auth_source_id):
    already_existing_users = db.session.query(LdapObject).filter(LdapObject.object_uuid == uuid).all()
    if len(already_existing_users) > 0:
        print("user already exists in ldapobject table")
        return already_existing_users[0]
    else:
        # Fetch user details from LDAP
        auth_source = db.session.query(AuthSource).filter_by(id=auth_source_id).first()
        if not auth_source:
            return None
        c = connect_to_ldap(auth_source.host, auth_source.bind_user_dn, auth_source.bind_password, port=auth_source.port, ssl=auth_source.ssl)
        if not c.bind():
            return None

        user = search_ldap(connection=c, base_dn=auth_source.base_dn, is_ad=auth_source.server_type == 'ad', uuid=uuid)
        if not user:
            return None
        user = user[0]
        ldap_object = LdapObject(
            auth_source_id=auth_source_id,
            object_type=user.get('type'),
            object_uuid=user.get('uuid'),
            name=user.get('name'),
            ldap_uid=user.get('id')
        )
        db.session.add(ldap_object)
        db.session.commit()
        return ldap_object
