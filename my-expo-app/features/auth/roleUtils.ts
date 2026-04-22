type GenericUser = Record<string, any> | null | undefined;

const normalize = (value: string) =>
  value
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .trim();

const collectFromObject = (value: any): string[] => {
  if (!value) return [];
  if (typeof value === 'string') return [value];
  if (Array.isArray(value)) {
    return value.flatMap(item => collectFromObject(item));
  }
  if (typeof value === 'object') {
    const candidates = [
      value.nombre,
      value.name,
      value.codigo,
      value.code,
      value.slug,
      value.rol,
      value.role,
      value.rol_nombre,
      value.role_name,
      value.tipo_usuario,
      value.user_type,
      value.perfil,
      value.profile,
    ];
    return candidates.filter((item): item is string => typeof item === 'string');
  }
  return [];
};

export const extractUserRoles = (user: GenericUser): string[] => {
  if (!user) return [];

  const directCandidates = [
    user.rol,
    user.role,
    user.rol_nombre,
    user.role_name,
    user.tipo,
    user.tipo_usuario,
    user.user_type,
    user.perfil,
    user.profile,
    user.empleado,
    user.empleado?.rol_nombre,
    user.empleado?.rol,
  ];

  const collectionCandidates = [user.roles, user.grupos, user.groups, user.perfiles, user.profiles];

  const directRoles = directCandidates
    .flatMap(item => collectFromObject(item))
    .filter(Boolean);

  const groupRoles = collectionCandidates
    .flatMap(item => collectFromObject(item))
    .filter(Boolean);

  return [...directRoles, ...groupRoles].map(normalize);
};

export const isCocinero = (user: GenericUser): boolean => {
  const roles = extractUserRoles(user);
  return roles.some(role => role.includes('cocinero') || role === 'cocina');
};
