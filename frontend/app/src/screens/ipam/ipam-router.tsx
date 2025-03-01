import { ButtonWithTooltip } from "@/components/buttons/button-with-tooltip";
import SlideOver from "@/components/display/slide-over";
import ObjectForm from "@/components/form/object-form";
import { Tabs } from "@/components/tabs";
import { DEFAULT_BRANCH_NAME } from "@/config/constants";
import useQuery from "@/hooks/useQuery";
import { getPermission } from "@/screens/permission/utils";
import { currentBranchAtom } from "@/state/atoms/branches.atom";
import { genericsState, schemaState } from "@/state/atoms/schema.atom";
import { constructPath } from "@/utils/fetch";
import { gql } from "@apollo/client";
import { Icon } from "@iconify-icon/react";
import { useAtomValue, useSetAtom } from "jotai";
import { useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { StringParam, useQueryParam } from "use-query-params";
import ErrorScreen from "../errors/error-screen";
import UnauthorizedScreen from "../errors/unauthorized-screen";
import { getObjectPermissionsQuery } from "../permission/queries/getObjectPermissions";
import { defaultIpNamespaceAtom } from "./common/namespace.state";
import {
  IPAM_QSP,
  IPAM_ROUTE,
  IPAM_TABS,
  IP_ADDRESS_GENERIC,
  IP_PREFIX_GENERIC,
} from "./constants";
import IpamIPAddresses from "./ip-addresses/ipam-ip-address";
import { reloadIpamTreeAtom } from "./ipam-tree/ipam-tree.state";
import IpamIPPrefixes from "./prefixes/ipam-prefixes";

const tabToKind = {
  [IPAM_TABS.IP_DETAILS]: IP_ADDRESS_GENERIC,
  [IPAM_TABS.PREFIX_DETAILS]: IP_PREFIX_GENERIC,
};

function IpamRouter() {
  const [qspTab] = useQueryParam(IPAM_QSP.TAB, StringParam);
  const navigate = useNavigate();
  const { prefix } = useParams();
  const branch = useAtomValue(currentBranchAtom);
  const schemaList = useAtomValue(schemaState);
  const genericList = useAtomValue(genericsState);
  const [namespace] = useQueryParam(IPAM_QSP.NAMESPACE, StringParam);
  const defaultIpNamespace = useAtomValue(defaultIpNamespaceAtom);
  const reloadIpamTree = useSetAtom(reloadIpamTreeAtom);
  const refetchRef = useRef(null);
  const [showCreateDrawer, setShowCreateDrawer] = useState(false);

  const objectname = qspTab ? tabToKind[qspTab] : IP_PREFIX_GENERIC;
  const schema = schemaList.find((s) => s.kind === objectname);
  const generic = genericList.find((s) => s.kind === objectname);
  const schemaData = schema || generic;

  const { loading, data, error } = useQuery(gql(getObjectPermissionsQuery(objectname)));

  const permission = data && getPermission(data?.[objectname]?.permissions?.edges);

  const tabs = [
    {
      label: "Summary",
      name: IPAM_TABS.SUMMARY,
      onClick: () => {
        if (prefix) {
          navigate(constructPath(`${IPAM_ROUTE.PREFIXES}/${prefix}`, [], [IPAM_QSP.NAMESPACE]));
          return;
        }

        navigate(constructPath(IPAM_ROUTE.PREFIXES, [], [IPAM_QSP.NAMESPACE]));
        return;
      },
    },
    {
      label: "Prefix Details",
      name: IPAM_TABS.PREFIX_DETAILS,
      onClick: () => {
        navigate(
          constructPath(
            prefix ? `${IPAM_ROUTE.PREFIXES}/${prefix}` : IPAM_ROUTE.PREFIXES,
            [{ name: IPAM_QSP.TAB, value: IPAM_TABS.PREFIX_DETAILS }],
            [IPAM_QSP.NAMESPACE]
          )
        );
        return;
      },
    },
    {
      label: "IP Details",
      name: IPAM_TABS.IP_DETAILS,
      onClick: () => {
        if (prefix) {
          navigate(
            constructPath(
              `${IPAM_ROUTE.PREFIXES}/${prefix}`,
              [{ name: IPAM_QSP.TAB, value: IPAM_TABS.IP_DETAILS }],
              [IPAM_QSP.NAMESPACE]
            )
          );
          return;
        }

        navigate(
          constructPath(
            IPAM_ROUTE.ADDRESSES,
            [{ name: IPAM_QSP.TAB, value: IPAM_TABS.IP_DETAILS }],
            [IPAM_QSP.NAMESPACE]
          )
        );
        return;
      },
    },
  ];

  const renderContent = () => {
    switch (qspTab) {
      case IPAM_TABS.IP_DETAILS: {
        return <IpamIPAddresses ref={refetchRef} />;
      }
      case IPAM_TABS.PREFIX_DETAILS:
      default: {
        return <IpamIPPrefixes ref={refetchRef} />;
      }
    }
  };

  if (error) {
    if (error.networkError?.statusCode === 403) {
      const { message } = error.networkError?.result?.errors?.[0] ?? {};

      return <UnauthorizedScreen message={message} />;
    }

    return <ErrorScreen message="Something went wrong when fetching IPAM details." />;
  }

  const rightitems = (
    <ButtonWithTooltip
      disabled={loading || !permission?.create.isAllowed}
      tooltipEnabled={!permission?.create.isAllowed}
      tooltipContent={permission?.create.message ?? undefined}
      onClick={() => setShowCreateDrawer(true)}
      className="mr-4"
      data-testid="create-object-button"
    >
      <Icon icon="mdi:plus" className="text-sm" />
      Add {schemaData?.label}
    </ButtonWithTooltip>
  );

  return (
    <>
      <Tabs tabs={tabs} qsp={IPAM_QSP.TAB} rightItems={rightitems} />

      <div className="p-3 flex flex-grow overflow-auto" data-testid="ipam-main-content">
        {renderContent()}
      </div>

      <SlideOver
        title={
          <div className="space-y-2">
            <div className="flex items-center w-full">
              <span className="text-lg font-semibold mr-3">Create {schemaData?.label}</span>
              <div className="flex-1"></div>
              <div className="flex items-center">
                <Icon icon={"mdi:layers-triple"} />
                <div className="ml-1.5 pb-1">{branch?.name ?? DEFAULT_BRANCH_NAME}</div>
              </div>
            </div>

            <div className="text-sm">{schemaData?.description}</div>

            <span className="inline-flex items-center rounded-md bg-yellow-50 px-2 py-1 text-xs font-medium text-yellow-800 ring-1 ring-inset ring-yellow-600/20 mr-2">
              <svg
                className="h-1.5 w-1.5 mr-1 fill-yellow-500"
                viewBox="0 0 6 6"
                aria-hidden="true"
              >
                <circle cx={3} cy={3} r={3} />
              </svg>
              {schemaData?.kind}
            </span>
          </div>
        }
        open={showCreateDrawer}
        setOpen={setShowCreateDrawer}
      >
        <ObjectForm
          kind={objectname}
          onSuccess={() => {
            refetchRef?.current?.refetch();
            setShowCreateDrawer(false);

            const currentIpNamespace = namespace ?? defaultIpNamespace;
            if (currentIpNamespace) {
              reloadIpamTree(currentIpNamespace, prefix);
            }
          }}
          onCancel={() => setShowCreateDrawer(false)}
        />
      </SlideOver>
    </>
  );
}

export function Component() {
  return <IpamRouter />;
}
