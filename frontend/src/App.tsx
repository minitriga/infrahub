import { useAtom, useAtomValue, useSetAtom } from "jotai";
import * as R from "ramda";
import { useEffect } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import { toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import { StringParam, useQueryParam } from "use-query-params";
import { ALERT_TYPES, Alert } from "./components/alert";
import { CONFIG } from "./config/config";
import { QSP } from "./config/qsp";
import { MAIN_ROUTES } from "./config/routes";
import { withAuth } from "./decorators/withAuth";
import Layout from "./screens/layout/layout";
import { branchesState, currentBranchAtom } from "./state/atoms/branches.atom";
import {
  currentSchemaHashAtom,
  genericsState,
  iGenericSchema,
  iNodeSchema,
  schemaState,
} from "./state/atoms/schema.atom";
import { schemaKindNameState } from "./state/atoms/schemaKindName.atom";
import "./styles/index.css";
import { sortByOrderWeight } from "./utils/common";
import { fetchUrl } from "./utils/fetch";
import mdiIcons from "@iconify-json/mdi/icons.json";
import { addCollection } from "@iconify-icon/react";
import { Branch } from "./generated/graphql";
addCollection(mdiIcons);

const sortByName = R.sortBy(R.compose(R.toLower, R.prop("name")));

function App() {
  const branches = useAtomValue(branchesState);
  const setCurrentBranch = useSetAtom(currentBranchAtom);
  const [, setSchema] = useAtom(schemaState);
  const [currentSchemaHash, setCurrentSchemaHash] = useAtom(currentSchemaHashAtom);
  const [, setGenerics] = useAtom(genericsState);
  const [, setSchemaKindNameState] = useAtom(schemaKindNameState);
  const [branchInQueryString] = useQueryParam(QSP.BRANCH, StringParam);

  /**
   * Fetch schema from the backend, and store it
   */
  const fetchAndSetSchema = async () => {
    try {
      const data: { main: string; nodes: iNodeSchema[]; generics: iGenericSchema[] } =
        await fetchUrl(CONFIG.SCHEMA_URL(branchInQueryString));

      const hash = data.main;
      const schema = sortByName(data.nodes || []);
      const generics = sortByName(data.generics || []);

      schema.forEach((s) => {
        s.attributes = sortByOrderWeight(s.attributes || []);
        s.relationships = sortByOrderWeight(s.relationships || []);
      });

      const schemaNames = R.map(R.prop("name"), schema);
      const schemaKinds = R.map(R.prop("kind"), schema);
      const schemaKindNameTuples = R.zip(schemaKinds, schemaNames);
      const schemaKindNameMap = R.fromPairs(schemaKindNameTuples);

      setGenerics(generics);
      setCurrentSchemaHash(hash);
      setSchema(schema);
      setSchemaKindNameState(schemaKindNameMap);
    } catch (error) {
      toast(
        <Alert type={ALERT_TYPES.ERROR} message="Something went wrong when fetching the schema" />
      );

      console.error("Error while fetching the schema: ", error);

      return {
        schema: [],
        generics: [],
      };
    }
  };

  const updateSchemaStateIfNeeded = async () => {
    try {
      const schemaSummary = await fetchUrl(CONFIG.SCHEMA_SUMMARY_URL(branchInQueryString));
      const isSameSchema = currentSchemaHash === schemaSummary.main;

      // Updating schema only if it's different from the current one
      if (isSameSchema) return;
      await fetchAndSetSchema();
    } catch (error) {
      console.error("Error while updating the schema state:", error);
    }
  };

  useEffect(() => {
    updateSchemaStateIfNeeded();
  }, [branchInQueryString]);

  useEffect(() => {
    const filter = branchInQueryString
      ? (b: Branch) => branchInQueryString === b.name
      : (b: Branch) => b.is_default;
    const selectedBranch = branches.find(filter);
    setCurrentBranch(selectedBranch);
  }, [branches.length, branchInQueryString]);

  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        {MAIN_ROUTES.map((route) => (
          <Route index key={route.path} path={route.path} element={route.element} />
        ))}
        <Route path="*" element={<Navigate to="/" />} />
      </Route>
    </Routes>
  );
}

export default withAuth(App);
