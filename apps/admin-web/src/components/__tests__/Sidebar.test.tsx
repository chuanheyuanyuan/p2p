import { describe, it, beforeEach, afterEach, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { act } from 'react';
import Sidebar from '../Sidebar';
import { useAuthStore } from '../../store/auth';

type PersistHelpers = {
  hasHydrated?: () => boolean;
  rehydrate?: () => Promise<void>;
};

const persistHelpers = (useAuthStore as typeof useAuthStore & { persist?: PersistHelpers }).persist;

const ensureHydrated = async () => {
  if (!persistHelpers || persistHelpers.hasHydrated?.()) return;
  await act(async () => {
    await persistHelpers.rehydrate?.();
  });
};

const renderSidebar = () =>
  render(
    <MemoryRouter initialEntries={['/collections']}>
      <Sidebar />
    </MemoryRouter>
  );

describe('Sidebar RBAC', () => {
  beforeEach(async () => {
    await ensureHydrated();
    localStorage.clear();
    await act(async () => {
      useAuthStore.setState((state) => ({
        ...state,
        accessToken: null,
        user: null,
        roles: [],
        permissions: []
      }));
    });
  });

  afterEach(async () => {
    await act(async () => {
      useAuthStore.getState().logout();
    });
    localStorage.clear();
  });

  it('shows only collector menus for collector role', async () => {
    await act(async () => {
      useAuthStore.setState((state) => ({
        ...state,
        accessToken: 'token',
        user: { id: 'collector', name: 'Collector Agent', email: 'collector@inscash.com' },
        roles: ['collector_agent'],
        permissions: ['collections:workbench']
      }));
    });

    await act(async () => {
      renderSidebar();
    });

    expect(screen.getByText('催收案件')).toBeInTheDocument();
    expect(screen.getByText('案件详情')).toBeInTheDocument();
    expect(screen.queryByText('申请管理')).not.toBeInTheDocument();
    expect(screen.queryByText('运营配置')).not.toBeInTheDocument();
  });

  it('falls back to empty state when no roles matched', async () => {
    await act(async () => {
      renderSidebar();
    });
    expect(screen.getByText('当前角色暂无菜单，请联系管理员。')).toBeInTheDocument();
  });
});
